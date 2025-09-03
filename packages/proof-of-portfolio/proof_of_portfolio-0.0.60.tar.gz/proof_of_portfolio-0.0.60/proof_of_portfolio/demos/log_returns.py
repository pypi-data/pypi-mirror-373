import os

import matplotlib.pyplot as plt
import numpy as np
from . import utils


def compare_implementations(test_data: dict):
    checkpoints = test_data["test_checkpoints"]
    target_duration = test_data["target_duration"]

    baseline_daily_returns = utils.LedgerUtils.daily_return_log(
        checkpoints, target_duration
    )

    circuit_daily_returns, circuit_valid_days = utils.run_nargo(
        test_data["gains"],
        test_data["losses"],
        test_data["last_update_times"],
        test_data["accum_times"],
        test_data["checkpoint_count"],
        target_duration,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "demo",
            "just_cps_to_log_return",
            "Prover.toml",
        ),
    )

    baseline_count = len(baseline_daily_returns)

    print(f"Miner ID: {test_data['miner_id']}")
    print(f"Checkpoint count: {test_data['checkpoint_count']}")
    print(f"Target duration: {target_duration}")
    print(f"Baseline daily returns count: {baseline_count}")
    print(f"Circuit daily returns count: {circuit_valid_days}")

    if baseline_count > 0:
        print(
            f"Baseline daily returns: {baseline_daily_returns[:5]}{'...' if baseline_count > 5 else ''}"
        )
    if circuit_valid_days > 0:
        print(
            f"Circuit daily returns: {circuit_daily_returns[:5]}{'...' if circuit_valid_days > 5 else ''}"
        )

    if baseline_count == circuit_valid_days and baseline_count > 0:
        diffs = [
            abs(b - c) for b, c in zip(baseline_daily_returns, circuit_daily_returns)
        ]
        max_diff = max(diffs)
        avg_diff = sum(diffs) / len(diffs)
        print(f"Max difference: {max_diff}")
        print(f"Average difference: {avg_diff}")

        return {
            "baseline": baseline_daily_returns,
            "circuit": circuit_daily_returns,
            "max_diff": max_diff,
            "avg_diff": avg_diff,
            "count_match": True,
        }
    else:
        print(
            f"Count mismatch! Baseline: {baseline_count}, Circuit: {circuit_valid_days}"
        )
        return {
            "baseline": baseline_daily_returns,
            "circuit": circuit_daily_returns,
            "max_diff": float("inf"),
            "avg_diff": float("inf"),
            "count_match": False,
        }


def run_batch_test(validator_data: dict, num_tests: int = 10):
    perf_ledgers = validator_data.get("perf_ledgers", {})
    miner_ids = list(perf_ledgers.keys())
    results = []

    for i in range(min(num_tests, len(miner_ids))):
        miner_id = miner_ids[i]
        test_data = utils.extract_test_data(validator_data, miner_id)

        if test_data:
            result = compare_implementations(test_data)
            results.append(result)
            print("---")

    if results:
        successful_results = [r for r in results if r["count_match"]]

        if successful_results:
            max_diffs = [r["max_diff"] for r in successful_results]
            avg_diffs = [r["avg_diff"] for r in successful_results]

            all_baseline_returns = []
            all_circuit_returns = []

            for r in successful_results:
                all_baseline_returns.extend(r["baseline"])
                all_circuit_returns.extend(r["circuit"])

            print(f"Batch test results ({len(successful_results)} successful tests):")
            print(f"Overall max difference: {max(max_diffs)}")
            print(f"Average max difference: {np.mean(max_diffs)}")
            print(f"Average avg difference: {np.mean(avg_diffs)}")
            print(f"Total daily returns compared: {len(all_baseline_returns)}")

            if len(all_baseline_returns) > 0:
                plt.figure(figsize=(15, 5))

                plt.subplot(1, 3, 1)
                plt.plot(all_baseline_returns[:100], "b-", label="Baseline", alpha=0.7)
                plt.plot(all_circuit_returns[:100], "r--", label="Circuit", alpha=0.7)
                plt.title("Baseline vs Circuit Returns (first 100)")
                plt.legend()

                plt.subplot(1, 3, 2)
                daily_diffs = [
                    abs(b - c)
                    for b, c in zip(all_baseline_returns, all_circuit_returns)
                ]
                plt.plot(daily_diffs[:100], "g-", alpha=0.7)
                plt.title("Daily Differences (first 100)")
                plt.ylabel("|Baseline - Circuit|")

                plt.subplot(1, 3, 3)
                plt.scatter(all_baseline_returns, all_circuit_returns, alpha=0.3, s=2)
                min_val = min(min(all_baseline_returns), min(all_circuit_returns))
                max_val = max(max(all_baseline_returns), max(all_circuit_returns))
                plt.plot([min_val, max_val], [min_val, max_val], "r--", alpha=0.8)
                plt.xlabel("Baseline")
                plt.ylabel("Circuit")
                plt.title("Circuit vs Baseline Scatter")

                plt.tight_layout()
                plt.show()
        else:
            print("No successful comparisons (all had count mismatches)")
    else:
        print("No results to analyze")


def main(args):
    validator_data = utils.load_validator_checkpoint_data()

    if not validator_data:
        print("Failed to load validator data")
        return

    if args.miner_id:
        test_data = utils.extract_test_data(
            validator_data, args.miner_id, args.max_checkpoints
        )
        if test_data:
            compare_implementations(test_data)
    else:
        run_batch_test(validator_data, args.batch_tests)
