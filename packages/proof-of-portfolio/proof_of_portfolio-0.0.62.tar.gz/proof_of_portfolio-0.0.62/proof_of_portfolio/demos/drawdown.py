import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from . import utils

SCALE = 10**18


class MinMetrics:
    @staticmethod
    def daily_max_drawdown(log_returns: list[float]) -> float:
        if len(log_returns) == 0:
            return 0.0

        cumulative_log_returns = np.cumsum(log_returns)
        running_max_log = np.maximum.accumulate(cumulative_log_returns)
        drawdowns = 1 - np.exp(cumulative_log_returns - running_max_log)
        max_drawdown = np.max(drawdowns)

        return max_drawdown


def run_drawdown_nargo(log_returns: list[float]):
    prover_path = os.path.join(
        os.path.dirname(__file__), "..", "demo", "just_drawdown", "Prover.toml"
    )

    padded_returns = log_returns + [0.0] * (120 - len(log_returns))

    with open(prover_path, "w") as f:
        f.write(f'n_returns = "{len(log_returns)}"\n')
        scaled_returns = [str(int(lr * SCALE)) for lr in padded_returns]
        f.write(f"log_returns = {scaled_returns}\n")

    result = subprocess.run(
        ["nargo", "execute"],
        capture_output=True,
        text=True,
        cwd=prover_path.rsplit("/", 1)[0],
    )

    if result.returncode != 0:
        print("Nargo execution failed:")
        print(result.stderr)
        raise RuntimeError("Nargo execution failed")

    try:
        output_line = [
            line for line in result.stdout.splitlines() if "Circuit output:" in line
        ][0]
        output_value_str = output_line.split(":")[1].strip()

        if "(" in output_value_str:
            output_value_str = output_value_str.split("(")[1].split(")")[0]

        if output_value_str.startswith("0x"):
            output_value = int(output_value_str, 16)
        else:
            output_value = int(output_value_str)

        if output_value >= 2**63:
            output_value -= 2**64

        return output_value / SCALE

    except (IndexError, ValueError) as e:
        print("Failed to parse Nargo output:")
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("Could not parse Nargo output") from e


def compare_implementations(test_data: dict):
    checkpoints = test_data["test_checkpoints"]
    target_duration = test_data["target_duration"]

    baseline_daily_returns = utils.LedgerUtils.daily_return_log(
        checkpoints, target_duration
    )

    if not baseline_daily_returns:
        print(
            f"Miner ID: {test_data['miner_id']} - No daily returns found, skipping drawdown calculation."
        )
        return None

    baseline_drawdown = MinMetrics.daily_max_drawdown(baseline_daily_returns)
    circuit_drawdown = run_drawdown_nargo(baseline_daily_returns)

    print(f"Miner ID: {test_data['miner_id']}")
    print(f"Daily returns count: {len(baseline_daily_returns)}")
    print(f"Baseline Max Drawdown: {baseline_drawdown}")
    print(f"Circuit Max Drawdown: {circuit_drawdown}")

    diff = abs(baseline_drawdown - circuit_drawdown)
    print(f"Difference: {diff}")

    return {
        "baseline": baseline_drawdown,
        "circuit": circuit_drawdown,
        "diff": diff,
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
            if result:
                results.append(result)
            print("---")

    if results:
        diffs = [r["diff"] for r in results]
        print(f"Batch test results ({len(results)} successful tests):")
        print(f"Max difference: {max(diffs)}")
        print(f"Average difference: {np.mean(diffs)}")

        baseline_results = [r["baseline"] for r in results]
        circuit_results = [r["circuit"] for r in results]

        plt.figure(figsize=(15, 5))
        plt.subplot(1, 2, 1)
        plt.plot(baseline_results, "b-", label="Baseline", alpha=0.7)
        plt.plot(circuit_results, "r--", label="Circuit", alpha=0.7)
        plt.title("Baseline vs Circuit Max Drawdown")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(diffs, "g-", alpha=0.7)
        plt.title("Differences")
        plt.ylabel("|Baseline - Circuit|")

        plt.tight_layout()
        plt.show()

    else:
        print("No results to analyze")


def main(args):
    validator_data = utils.load_validator_checkpoint_data()

    if not validator_data:
        print("Failed to load validator data")
        return

    run_batch_test(validator_data, args.batch_tests)
