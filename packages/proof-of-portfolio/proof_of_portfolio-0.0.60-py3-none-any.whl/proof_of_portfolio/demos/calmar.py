import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
import time
from . import utils
from ..parsing_utils import parse_demo_output

SCALE = 10_000_000
WEIGHTED_AVERAGE_DECAY_RATE = 0.08
WEIGHTED_AVERAGE_DECAY_MIN = 0.40
WEIGHTED_AVERAGE_DECAY_MAX = 1.0
ANNUAL_RISK_FREE_PERCENTAGE = 4.19
DAYS_IN_YEAR = 365
ANNUAL_RISK_FREE_DECIMAL = ANNUAL_RISK_FREE_PERCENTAGE / 100
CALMAR_NOCONFIDENCE_VALUE = -100
STATISTICAL_CONFIDENCE_MINIMUM_N = 30


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
    def average(log_returns, weighting=False, indices=None):
        if len(log_returns) == 0:
            return 0.0
        weighting_distribution = MinMetrics.weighting_distribution(log_returns)
        if indices is not None and len(indices) != 0:
            indices = [i for i in indices if i in range(len(log_returns))]
            log_returns = [log_returns[i] for i in indices]
            weighting_distribution = [weighting_distribution[i] for i in indices]
        if weighting:
            avg_value = np.average(log_returns, weights=weighting_distribution)
        else:
            avg_value = np.mean(log_returns)
        return float(avg_value)

    @staticmethod
    def ann_excess_return(log_returns, weighting=False):
        annual_risk_free_rate = ANNUAL_RISK_FREE_DECIMAL
        days_in_year = DAYS_IN_YEAR
        if len(log_returns) == 0:
            return 0.0
        annualized_excess_return = (
            MinMetrics.average(log_returns, weighting=weighting) * days_in_year
        ) - annual_risk_free_rate
        return annualized_excess_return

    @staticmethod
    def daily_max_drawdown(log_returns: list[float]) -> float:
        if len(log_returns) == 0:
            return 0.0

        cumulative_log_returns = np.cumsum(log_returns)
        running_max_log = np.maximum.accumulate(cumulative_log_returns)
        drawdowns = 1 - np.exp(cumulative_log_returns - running_max_log)
        max_drawdown = np.max(drawdowns)
        return max_drawdown

    @staticmethod
    def calmar(log_returns, bypass_confidence=False, weighting=False, **kwargs):
        if len(log_returns) < STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return CALMAR_NOCONFIDENCE_VALUE

        ann_excess_return = MinMetrics.ann_excess_return(
            log_returns, weighting=weighting
        )
        max_drawdown = MinMetrics.daily_max_drawdown(log_returns)

        if max_drawdown == 0:
            return 0.0
        else:
            return float(ann_excess_return / max_drawdown)


def run_calmar_nargo(
    log_returns: list[float], bypass_confidence: bool, weighting: bool
):
    prover_path = os.path.join(
        os.path.dirname(__file__), "..", "demo", "just_calmar", "Prover.toml"
    )

    padded_returns = log_returns + [0.0] * (120 - len(log_returns))
    print(f"DEBUG: Writing to Prover.toml - first 5 returns: {log_returns[:5]}")

    with open(prover_path, "w") as f:
        f.write(f'actual_len = "{len(log_returns)}"\n')
        f.write(f'bypass_confidence = "{int(bypass_confidence)}"\n')
        scaled_returns = [str(int(lr * SCALE)) for lr in padded_returns]
        f.write(f"log_returns = {scaled_returns}\n")
        f.write(f'risk_free_rate = "{int(ANNUAL_RISK_FREE_DECIMAL * SCALE)}"\n')
        f.write(f'use_weighting = "{int(weighting)}"\n')
        f.flush()
        os.fsync(f.fileno())

    # Add small delay to ensure file is fully written
    time.sleep(0.1)

    # Debug: Show absolute path and verify file exists
    abs_path = os.path.abspath(prover_path)
    print(f"DEBUG: Using absolute path: {abs_path}")
    print(f"DEBUG: File exists: {os.path.exists(abs_path)}")

    result = subprocess.run(
        ["nargo", "execute"],
        capture_output=True,
        text=True,
        cwd=prover_path.rsplit("/", 1)[0],
    )

    # Debug: Check what's in Prover.toml after nargo execute
    with open(prover_path, "r") as f:
        content = f.read()
        print(
            f"DEBUG: Prover.toml after nargo execute - first line of log_returns: {content.split('log_returns = [')[1].split(',')[0] if 'log_returns = [' in content else 'NOT_FOUND'}"
        )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("nargo execute failed")

    fp = parse_demo_output(result.stdout, SCALE, CALMAR_NOCONFIDENCE_VALUE)

    # Debug: Final check of Prover.toml at end of function
    with open(prover_path, "r") as f:
        content = f.read()
        print(
            f"DEBUG: Prover.toml at end of function - first line of log_returns: {content.split('log_returns = [')[1].split(',')[0] if 'log_returns = [' in content else 'NOT_FOUND'}"
        )

    return fp


def compare_implementations(test_data: dict, bypass_confidence: bool, weighting: bool):
    checkpoints = test_data["test_checkpoints"]
    target_duration = test_data["target_duration"]

    baseline_daily_returns = utils.LedgerUtils.daily_return_log(
        checkpoints, target_duration
    )

    if not baseline_daily_returns:
        print(
            f"Miner ID: {test_data['miner_id']} - No daily returns found, skipping Calmar calculation."
        )
        return None

    print(
        f"DEBUG: Miner {test_data['miner_id']} log_returns[:5]: {baseline_daily_returns[:5]}"
    )

    baseline_calmar = MinMetrics.calmar(
        baseline_daily_returns, bypass_confidence, weighting
    )

    # Debug: Calculate individual components
    baseline_excess_return = MinMetrics.ann_excess_return(
        baseline_daily_returns, weighting=weighting
    )
    baseline_max_drawdown = MinMetrics.daily_max_drawdown(baseline_daily_returns)
    print(
        f"DEBUG: Baseline excess_return={baseline_excess_return:.6f}, max_drawdown={baseline_max_drawdown:.6f}"
    )

    circuit_calmar = run_calmar_nargo(
        baseline_daily_returns, bypass_confidence, weighting
    )

    print(f"Miner ID: {test_data['miner_id']}")
    print(f"Daily returns count: {len(baseline_daily_returns)}")
    print(f"Baseline Calmar: {baseline_calmar}")
    print(f"Circuit Calmar: {circuit_calmar}")

    diff = abs(baseline_calmar - circuit_calmar)
    print(f"Difference: {diff}")

    return {
        "baseline": baseline_calmar,
        "circuit": circuit_calmar,
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
        plt.title("Baseline vs Circuit Calmar Ratios")
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
