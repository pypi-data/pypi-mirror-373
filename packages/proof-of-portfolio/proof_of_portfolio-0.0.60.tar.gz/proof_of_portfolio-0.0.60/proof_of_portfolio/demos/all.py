import time
from . import utils, sharpe, omega, sortino, calmar, tstat, drawdown, log_returns


def run_all_demos(
    validator_data: dict,
    num_tests: int = 10,
    bypass_confidence: bool = False,
    weighting: bool = False,
):
    """Run all demos sequentially with the same parameters"""

    demos = [
        ("Sharpe", sharpe),
        ("Omega", omega),
        ("Sortino", sortino),
        ("Calmar", calmar),
        ("T-Stat", tstat),
        ("Drawdown", drawdown),
        ("Log Returns", log_returns),
    ]

    print("=" * 80)
    print("RUNNING ALL DEMOS SEQUENTIALLY")
    print("=" * 80)
    print("Configuration:")
    print(f"  - Batch tests: {num_tests}")
    print(f"  - Bypass confidence: {bypass_confidence}")
    print(f"  - Use weighting: {weighting}")
    print("=" * 80)

    results_summary = []

    for demo_name, demo_module in demos:
        print(f"\n{'=' * 20} {demo_name.upper()} DEMO {'=' * 20}")
        start_time = time.time()

        try:
            # Create a mock args object with the required attributes
            class MockArgs:
                def __init__(
                    self,
                    batch_tests,
                    bypass_confidence,
                    weighting,
                    miner_id=None,
                    max_checkpoints=200,
                ):
                    self.batch_tests = batch_tests
                    self.bypass_confidence = bypass_confidence
                    self.weighting = weighting
                    self.miner_id = miner_id
                    self.max_checkpoints = max_checkpoints

            mock_args = MockArgs(num_tests, bypass_confidence, weighting)

            # Call the demo's main function
            demo_module.main(mock_args)

            end_time = time.time()
            duration = end_time - start_time

            results_summary.append(
                {"demo": demo_name, "status": "✅ SUCCESS", "duration": duration}
            )

            print(f"\n{demo_name} demo completed successfully in {duration:.2f}s")

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            results_summary.append(
                {
                    "demo": demo_name,
                    "status": f"❌ FAILED: {str(e)}",
                    "duration": duration,
                }
            )

            print(f"\n{demo_name} demo failed after {duration:.2f}s: {str(e)}")

        print("=" * (42 + len(demo_name)))

    # Print summary
    print(f"\n{'=' * 80}")
    print("DEMO SUMMARY")
    print("=" * 80)

    total_time = sum(r["duration"] for r in results_summary)
    successful_demos = sum(1 for r in results_summary if "SUCCESS" in r["status"])

    for result in results_summary:
        print(
            f"{result['demo']:<15} | {result['status']:<30} | {result['duration']:.2f}s"
        )

    print("-" * 80)
    print(f"Total demos: {len(results_summary)}")
    print(f"Successful: {successful_demos}")
    print(f"Failed: {len(results_summary) - successful_demos}")
    print(f"Total time: {total_time:.2f}s")
    print("=" * 80)


def main(args):
    validator_data = utils.load_validator_checkpoint_data()

    if not validator_data:
        print("Failed to load validator data")
        return

    run_all_demos(
        validator_data, args.batch_tests, args.bypass_confidence, args.weighting
    )
