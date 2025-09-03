import json
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from .miner import Miner


def parse_order_string(order_str: str) -> Optional[Dict[str, Any]]:
    """
    Parse order string by replacing PriceSource with dict and using eval with restricted globals
    """
    try:
        cleaned_str = order_str.replace("PriceSource(", "dict(")
        order_data = eval(cleaned_str)
        return order_data

    except Exception as e:
        print(f"Failed to parse order string: {e}", file=sys.stderr)
        return None


def load_processed_signals(signals_path: Path) -> List[Dict[str, Any]]:
    """Load and parse all processed signal files from directory"""
    signals = []

    for signal_file in [
        f
        for f in signals_path.glob("*")
        if os.path.isfile(f) and "." not in os.path.basename(f)
    ]:
        try:
            with open(signal_file, "r") as f:
                f_str = f.read()
                f_str.replace("PriceSource", "dict")

                signal_data = eval(f_str)
                signals.append(signal_data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not parse {signal_file}: {e}", file=sys.stderr)
            continue

    return signals


def sort_signals_chronologically(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort signals by processing_timestamp in chronological order"""
    return sorted(signals, key=lambda x: x.get("processing_timestamp", ""))


def extract_validator_orders(
    signals: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Extract orders for each validator from chronologically sorted signals"""
    validator_orders = {}

    for signal in signals:
        created_orders = signal.get("created_orders", {})
        for validator_key, order_str in created_orders.items():
            if validator_key not in validator_orders:
                validator_orders[validator_key] = []

            try:
                order_data = parse_order_string(order_str)

                if order_data:
                    order_data["signal_timestamp"] = signal.get("processing_timestamp")
                    validator_orders[validator_key].append(order_data)
            except Exception as e:
                print(
                    f"Could not parse order for validator {validator_key}: {e}",
                    file=sys.stderr,
                )

    return validator_orders


def generate_validator_trees(
    signals_dir: str,
    hotkey: Optional[str] = None,
    output_dir: Optional[str] = None,
    quiet: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Generate merkle trees for all validators from processed mining signals.

    Args:
        signals_dir: Directory containing processed signal JSON files
        hotkey: Optional hotkey to use for tree generation
        output_dir: Optional directory to save tree files
        quiet: Whether to suppress output messages

    Returns:
        Dictionary mapping validator keys to tree data and metadata
    """
    signals_path = Path(signals_dir)
    if not signals_path.exists() or not signals_path.is_dir():
        if not quiet:
            print(
                f"Error: Signals directory not found at {signals_dir}", file=sys.stderr
            )
        return {}

    if not quiet:
        print(f"Loading processed signals from {signals_dir}")

    signals = load_processed_signals(signals_path)
    if not signals:
        if not quiet:
            print("Error: No valid signal files found in directory", file=sys.stderr)
        return {}

    if not quiet:
        print(f"Loaded {len(signals)} signal files")

    sorted_signals = sort_signals_chronologically(signals)

    validator_orders = extract_validator_orders(sorted_signals)

    if not validator_orders:
        if not quiet:
            print("Error: No validator orders found in signals", file=sys.stderr)
        return {}

    if not quiet:
        print(f"Found orders for {len(validator_orders)} validators")

    validator_trees = {}

    for validator_key, orders in validator_orders.items():
        if not quiet:
            print(
                f"Generating tree for validator {validator_key[:8]}... ({len(orders)} orders)"
            )

        temp_data = {"positions": [{"orders": orders}]}

        validator_hotkey = hotkey or validator_key

        miner = Miner(validator_hotkey, f"Validator-{validator_key[:8]}")

        if output_dir:
            validator_output = str(Path(output_dir) / f"tree_{validator_key[:8]}.json")
        else:
            validator_output = str(signals_path / f"tree_{validator_key[:8]}.json")

        temp_file = signals_path / f"temp_{validator_key[:8]}.json"
        try:
            with open(temp_file, "w") as f:
                json.dump(temp_data, f, indent=2)

            tree_data = miner.generate_tree(str(temp_file), validator_output)

            if tree_data:
                tree_hash = (
                    tree_data.get("merkle_root")
                    or tree_data.get("root_hash")
                    or tree_data.get("hash")
                    or "unknown"
                )

                validator_trees[validator_key] = {
                    "tree_data": tree_data,
                    "output_path": validator_output,
                    "order_count": len(orders),
                    "tree_hash": tree_hash,
                }
                if not quiet:
                    print(
                        f"✓ Generated tree for validator {validator_key[:8]} - Hash: {tree_hash[:16]}..."
                    )
            else:
                if not quiet:
                    print(
                        f"✗ Failed to generate tree for validator {validator_key[:8]}"
                    )

        finally:
            if temp_file.exists():
                temp_file.unlink()

    if not quiet:
        print(f"\nSuccessfully generated trees for {len(validator_trees)} validators")
        print(
            f"Processed {len(signals)} signal files with {sum(len(orders) for orders in validator_orders.values())} total orders"
        )

    return validator_trees


def get_validator_tree_hashes(
    validator_trees: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    """
    Extract tree hashes for each validator for verification purposes.

    Args:
        validator_trees: Dictionary of validator tree data from generate_validator_trees

    Returns:
        Dictionary mapping validator keys to their tree hashes
    """
    return {
        validator_key: data["tree_hash"]
        for validator_key, data in validator_trees.items()
    }
