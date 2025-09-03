# This file makes the src directory a Python package

import os
import shutil
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import wraps

_dependencies_checked = False


def ensure_dependencies():
    """Ensure bb and nargo are installed before running package functions."""
    global _dependencies_checked

    if (
        _dependencies_checked
        or os.environ.get("CI")
        or os.environ.get("POP_SKIP_INSTALL")
    ):
        return

    missing_deps = []
    if not shutil.which("bb"):
        missing_deps.append("bb")
    if not shutil.which("nargo"):
        missing_deps.append("nargo")

    if missing_deps:
        print(f"Installing required dependencies: {', '.join(missing_deps)}...")
        print("This may take a few minutes on first run.")

        try:
            from .post_install import main as post_install_main

            post_install_main()
            print("Dependencies installed successfully!")
        except Exception as e:
            print(f"Warning: Failed to install dependencies: {e}")

    _dependencies_checked = True


def requires_dependencies(func):
    """Decorator to ensure dependencies are installed before running a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        ensure_dependencies()
        return func(*args, **kwargs)

    return wrapper


def _prove_worker(
    miner_data,
    hotkey,
    verbose=False,
    annual_risk_free_percentage=4.19,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
):
    """
    Worker function to run proof generation in a separate process.
    """
    try:
        from .proof_generator import generate_proof

        result = generate_proof(
            miner_data,
            hotkey,
            verbose=verbose,
            annual_risk_free_percentage=annual_risk_free_percentage,
            use_weighting=use_weighting,
            bypass_confidence=bypass_confidence,
            daily_checkpoints=daily_checkpoints,
        )

        return {
            "status": "success",
            "portfolio_metrics": result.get("portfolio_metrics", {}),
            "merkle_roots": result.get("merkle_roots", {}),
            "data_summary": result.get("data_summary", {}),
            "proof_results": result.get("proof_results", {}),
            "proof_generated": result.get("proof_results", {}).get(
                "proof_generated", False
            ),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "proof_generated": False,
        }


@requires_dependencies
async def prove(
    miner_data,
    hotkey,
    verbose=False,
    annual_risk_free_percentage=4.19,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
):
    """
    Generate zero-knowledge proof for miner portfolio data asynchronously.

    Args:
        miner_data: Dictionary containing perf_ledgers and positions for the miner
        hotkey: Miner's hotkey
        verbose: Boolean to control logging verbosity

    Returns:
        Dictionary with proof results including status, portfolio_metrics, etc.
    """
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=1) as executor:
        try:
            result = await loop.run_in_executor(
                executor,
                _prove_worker,
                miner_data,
                hotkey,
                verbose,
                annual_risk_free_percentage,
                use_weighting,
                bypass_confidence,
                daily_checkpoints,
            )
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "proof_generated": False,
            }


def prove_sync(
    miner_data,
    hotkey,
    verbose=False,
    annual_risk_free_percentage=4.19,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
):
    """
    Synchronous wrapper for the prove function for backward compatibility.

    Args:
        miner_data: Dictionary containing perf_ledgers and positions for the miner
        hotkey: Miner's hotkey
        verbose: Boolean to control logging verbosity

    Returns:
        Dictionary with proof results including status, portfolio_metrics, etc.
    """
    return _prove_worker(
        miner_data,
        hotkey,
        verbose,
        annual_risk_free_percentage,
        use_weighting,
        bypass_confidence,
        daily_checkpoints,
    )
