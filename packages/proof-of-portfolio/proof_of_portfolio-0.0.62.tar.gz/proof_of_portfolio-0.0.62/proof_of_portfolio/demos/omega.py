import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from . import utils
from ..parsing_utils import parse_demo_output

SCALE = 10_000_000
WEIGHTED_AVERAGE_DECAY_RATE = 0.08
WEIGHTED_AVERAGE_DECAY_MIN = 0.40
WEIGHTED_AVERAGE_DECAY_MAX = 1.0
OMEGA_LOSS_MINIMUM = 0.01
STATISTICAL_CONFIDENCE_MINIMUM_N = 60
OMEGA_NOCONFIDENCE_VALUE = -100


class MinMetrics:
    @staticmethod
    def weighting_distribution(log_returns):
        max_weight = WEIGHTED_AVERAGE_DECAY_MAX
        min_weight = WEIGHTED_AVERAGE_DECAY_MIN
        decay_rate = WEIGHTED_AVERAGE_DECAY_RATE
        if len(log_returns) < 1:
            return np.ones(0)
        weighting_distribution_days = np.arange(0, len(log_returns))
        weight_range = max_weight - min_weight
        decay_values = min_weight + (
            weight_range * np.exp(-decay_rate * weighting_distribution_days)
        )
        return decay_values[::-1][-len(log_returns) :]

    @staticmethod
    def omega(log_returns, bypass_confidence=False, weighting=False, **kwargs):
        if len(log_returns) < STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return OMEGA_NOCONFIDENCE_VALUE

        if weighting:
            weighing_array = MinMetrics.weighting_distribution(log_returns)

            positive_indices = []
            negative_indices = []
            product_sum_positive = product_sum_negative = 0
            sum_of_weights_positive = sum_of_weights_negative = OMEGA_LOSS_MINIMUM

            for c, log_return in enumerate(log_returns):
                if log_return > 0:
                    positive_indices.append(c)
                else:
                    negative_indices.append(c)

            log_return_arr = np.array(log_returns)

            if len(positive_indices) > 0:
                positive_indices_arr = np.array(positive_indices)
                sum_of_weights_positive = max(
                    np.sum(weighing_array[positive_indices_arr]), OMEGA_LOSS_MINIMUM
                )

                product_sum_positive = np.sum(
                    np.multiply(
                        log_return_arr[positive_indices_arr],
                        weighing_array[positive_indices_arr],
                    )
                )

            if len(negative_indices) > 0:
                negative_indices_arr = np.array(negative_indices)
                sum_of_weights_negative = max(
                    np.sum(weighing_array[negative_indices_arr]), OMEGA_LOSS_MINIMUM
                )
                product_sum_negative = np.sum(
                    np.multiply(
                        log_return_arr[negative_indices_arr],
                        weighing_array[negative_indices_arr],
                    )
                )

            positive_sum = product_sum_positive * sum_of_weights_negative
            negative_sum = product_sum_negative * sum_of_weights_positive

        else:
            positive_sum = 0
            negative_sum = 0

            for log_return in log_returns:
                if log_return > 0:
                    positive_sum += log_return
                else:
                    negative_sum += log_return

        numerator = positive_sum
        denominator = max(abs(negative_sum), OMEGA_LOSS_MINIMUM)

        return float(numerator / denominator)


def run_omega_nargo(log_returns: list[float], bypass_confidence: bool, weighting: bool):
    prover_path = os.path.join(
        os.path.dirname(__file__), "..", "demo", "just_omega", "Prover.toml"
    )

    padded_returns = log_returns + [0.0] * (120 - len(log_returns))

    with open(prover_path, "w") as f:
        f.write(f'actual_len = "{len(log_returns)}"\n')
        f.write(f'bypass_confidence = "{int(bypass_confidence)}"\n')
        scaled_returns = [str(int(lr * SCALE)) for lr in padded_returns]
        f.write(f"log_returns = {scaled_returns}\n")
        f.write(f'use_weighting = "{int(weighting)}"\n')

    result = subprocess.run(
        ["nargo", "execute"],
        capture_output=True,
        text=True,
        cwd=prover_path.rsplit("/", 1)[0],
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("nargo execute failed")

    return parse_demo_output(result.stdout, SCALE, OMEGA_NOCONFIDENCE_VALUE)


def compare_implementations(test_data: dict, bypass_confidence: bool, weighting: bool):
    checkpoints = test_data["test_checkpoints"]
    target_duration = test_data["target_duration"]

    baseline_daily_returns = utils.LedgerUtils.daily_return_log(
        checkpoints, target_duration
    )

    if not baseline_daily_returns:
        print(
            f"Miner ID: {test_data['miner_id']} - No daily returns found, skipping Omega calculation."
        )
        return None

    baseline_omega = MinMetrics.omega(
        baseline_daily_returns, bypass_confidence, weighting
    )
    circuit_omega = run_omega_nargo(
        baseline_daily_returns, bypass_confidence, weighting
    )

    print(f"Miner ID: {test_data['miner_id']}")
    print(f"Daily returns count: {len(baseline_daily_returns)}")
    print(f"Baseline Omega: {baseline_omega}")
    print(f"Circuit Omega: {circuit_omega}")

    diff = abs(baseline_omega - circuit_omega)
    print(f"Difference: {diff}")

    return {
        "baseline": baseline_omega,
        "circuit": circuit_omega,
        "diff": diff,
    }


def run_batch_test(
    validator_data: dict,
    num_tests: int = 10,
    bypass_confidence: bool = False,
    weighting: bool = False,
):
    perf_ledgers = validator_data.get("perf_ledgers", {})
    miner_ids = list(perf_ledgers.keys())
    results = []

    for i in range(min(num_tests, len(miner_ids))):
        miner_id = miner_ids[i]
        test_data = utils.extract_test_data(validator_data, miner_id)

        if test_data:
            result = compare_implementations(test_data, bypass_confidence, weighting)
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
        plt.title("Baseline vs Circuit Omega Ratios")
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

    run_batch_test(
        validator_data, args.batch_tests, args.bypass_confidence, args.weighting
    )
