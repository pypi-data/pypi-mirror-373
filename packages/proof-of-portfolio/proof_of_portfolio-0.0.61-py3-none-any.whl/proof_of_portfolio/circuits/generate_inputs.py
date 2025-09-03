#!/usr/bin/env python3

import json
import sys
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Tuple

COMPUTED_RETURNS_MERKLE_ROOT = (
    "11867626551045947428625699719016106318414315494538029175888081011781332338787"
)

SCALE = 10_000_000  # Same scale as used in the circuit
MAX_SIGNALS = 256


def load_validator_checkpoint(file_path: str) -> Dict[str, Any]:
    """Load and parse the validator checkpoint JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def extract_checkpoint_data(
    checkpoint_data: Dict[str, Any], miner_hotkey: str
) -> Dict[str, Any]:
    """Extract checkpoint data for a specific miner."""
    if miner_hotkey not in checkpoint_data["perf_ledgers"]:
        raise ValueError(f"Miner {miner_hotkey} not found in checkpoint data")

    miner_data = checkpoint_data["perf_ledgers"][miner_hotkey]
    checkpoints = miner_data["cps"]
    target_duration = miner_data["target_cp_duration_ms"]

    gains = []
    losses = []
    last_update_times = []
    accum_times = []

    for cp in checkpoints:
        # Convert gains and losses to scaled integers
        gain_scaled = int(cp["gain"] * SCALE)
        loss_scaled = int(cp["loss"] * SCALE)

        gains.append(str(gain_scaled))
        losses.append(str(loss_scaled))
        last_update_times.append(str(cp["last_update_ms"]))
        accum_times.append(str(cp["accum_ms"]))

    return {
        "gains": gains,
        "losses": losses,
        "last_update_times": last_update_times,
        "accum_times": accum_times,
        "checkpoint_count": len(checkpoints),
        "target_duration": target_duration,
    }


def extract_trading_signals(
    checkpoint_data: Dict[str, Any], miner_hotkey: str
) -> List[Dict[str, Any]]:
    """Extract trading signals from position data for a specific miner."""
    if miner_hotkey not in checkpoint_data["positions"]:
        print(f"Warning: No position data found for miner {miner_hotkey}")
        return []

    miner_positions = checkpoint_data["positions"][miner_hotkey]["positions"]
    signals = []

    # Extract signals from orders in positions
    for position in miner_positions:
        for order in position["orders"]:
            # Map order_type to integer
            order_type_map = {"LONG": 1, "SHORT": 2, "FLAT": 0}

            # Get trade pair ID (using first element of trade_pair array as identifier)
            trade_pair_id = hash(position["trade_pair"][0]) % (
                2**31
            )  # Simple hash to Field

            signal = {
                "trade_pair_id": str(trade_pair_id),
                "order_type": str(order_type_map.get(order["order_type"], 0)),
                "leverage": str(
                    int(abs(order.get("leverage", 0)) * 1000)
                ),  # Scale and make positive
                "timestamp": str(order["processed_ms"]),
            }
            signals.append(signal)

    # Limit to MAX_SIGNALS and pad if necessary
    signals = signals[:MAX_SIGNALS]

    # Pad with zero signals if needed
    while len(signals) < MAX_SIGNALS:
        signals.append(
            {"trade_pair_id": "0", "order_type": "0", "leverage": "0", "timestamp": "0"}
        )

    return signals


def create_signals_toml(signals: List[Dict[str, Any]]) -> str:
    """Create TOML content for signals to use with tree_generator."""
    signals_toml = ""

    for i, signal in enumerate(signals):
        signals_toml += f"""
[[signals]]
trade_pair_id = "{signal['trade_pair_id']}"
order_type = "{signal['order_type']}"
leverage = "{signal['leverage']}"
timestamp = "{signal['timestamp']}"
"""

    toml_content = f"""
actual_len = "{len([s for s in signals if s['trade_pair_id'] != '0'])}"
{signals_toml}
"""

    return toml_content


def run_tree_generator(
    signals: List[Dict[str, Any]],
) -> Tuple[str, List[List[str]], List[List[str]]]:
    """Run the tree_generator to create merkle tree and get proofs."""

    # Create temporary TOML file for tree_generator
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        toml_content = create_signals_toml(signals)
        f.write(toml_content)
        temp_toml_path = f.name

    try:
        # Change to tree_generator directory and run it
        original_cwd = os.getcwd()
        tree_gen_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tree_generator",
        )

        # Copy temp file to tree_generator/Prover.toml
        tree_prover_path = os.path.join(tree_gen_path, "Prover.toml")
        with open(temp_toml_path, "r") as src, open(tree_prover_path, "w") as dst:
            dst.write(src.read())

        os.chdir(tree_gen_path)

        # Run nargo execute to get the merkle tree data
        result = subprocess.run(["nargo", "execute"], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Tree generator failed: {result.stderr}")

        # Parse the output to extract merkle root and paths
        # For now, we'll use a placeholder implementation
        # In practice, you'd parse the actual output from the tree_generator

        signals_merkle_root = "0"  # Placeholder - would extract from actual output

        # Create placeholder path elements and indices
        path_elements = []
        path_indices = []

        for i in range(MAX_SIGNALS):
            path_elements.append(["0"] * 8)  # MERKLE_DEPTH = 8
            path_indices.append(["0"] * 8)

        return signals_merkle_root, path_elements, path_indices

    finally:
        os.chdir(original_cwd)
        os.unlink(temp_toml_path)
        if os.path.exists(tree_prover_path):
            os.unlink(tree_prover_path)


def pad_arrays(data: Dict[str, Any], max_size: int = 200) -> Dict[str, Any]:
    """Pad arrays to the maximum size expected by the circuit."""
    for key in ["gains", "losses", "last_update_times", "accum_times"]:
        while len(data[key]) < max_size:
            data[key].append("0")
    return data


def format_2d_array_for_toml(arr: List[List[str]], name: str) -> str:
    """Format 2D array for TOML."""
    lines = [f"{name} = ["]
    for row in arr:
        formatted_row = "[" + ", ".join(f'"{item}"' for item in row) + "]"
        lines.append(f"    {formatted_row},")
    lines.append("]")
    return "\n".join(lines)


def generate_prover_toml(
    checkpoint_file_path: str = "../validator_checkpoint.json", miner_hotkey: str = None
) -> str:
    """Generate Prover.toml content from checkpoint data."""

    # Load checkpoint data
    checkpoint_data = load_validator_checkpoint(checkpoint_file_path)

    # Get first available miner if none specified
    if miner_hotkey is None:
        available_miners = list(checkpoint_data["perf_ledgers"].keys())
        if not available_miners:
            raise ValueError("No miners found in checkpoint data")
        miner_hotkey = available_miners[0]
        print(f"Using miner: {miner_hotkey}")

    # Extract checkpoint data
    circuit_data = extract_checkpoint_data(checkpoint_data, miner_hotkey)
    circuit_data = pad_arrays(circuit_data)

    # Extract trading signals
    signals = extract_trading_signals(checkpoint_data, miner_hotkey)
    actual_signals_count = len([s for s in signals if s["trade_pair_id"] != "0"])
    print(f"Extracted {actual_signals_count} trading signals")

    # Generate merkle tree for signals
    try:
        signals_merkle_root, path_elements, path_indices = run_tree_generator(signals)
    except Exception as e:
        print(f"Warning: Tree generator failed: {e}")
        print("Using placeholder values for merkle data")
        signals_merkle_root = "0"
        path_elements = [["0"] * 8 for _ in range(MAX_SIGNALS)]
        path_indices = [["0"] * 8 for _ in range(MAX_SIGNALS)]

    # Format arrays for TOML
    gains_array = "[" + ", ".join(f'"{g}"' for g in circuit_data["gains"]) + "]"
    losses_array = "[" + ", ".join(f'"{l}"' for l in circuit_data["losses"]) + "]"
    last_update_times_array = (
        "[" + ", ".join(f'"{t}"' for t in circuit_data["last_update_times"]) + "]"
    )
    accum_times_array = (
        "[" + ", ".join(f'"{t}"' for t in circuit_data["accum_times"]) + "]"
    )

    # Format signals array
    signals_toml = "signals = [\n"
    for signal in signals:
        signals_toml += f"""    {{ trade_pair_id = "{signal['trade_pair_id']}", order_type = "{signal['order_type']}", leverage = "{signal['leverage']}", timestamp = "{signal['timestamp']}" }},\n"""
    signals_toml += "]"

    # Format 2D arrays
    path_elements_toml = format_2d_array_for_toml(path_elements, "path_elements")
    path_indices_toml = format_2d_array_for_toml(path_indices, "path_indices")

    toml_content = f"""# Generated test inputs for portfolio proof circuit
# Miner: {miner_hotkey}
# Checkpoints: {circuit_data['checkpoint_count']}
# Signals: {actual_signals_count}

# Checkpoint data arrays
gains = {gains_array}

losses = {losses_array}

last_update_times = {last_update_times_array}

accum_times = {accum_times_array}

# Trading signals
{signals_toml}

# Merkle proof data
{path_elements_toml}

{path_indices_toml}

# Circuit parameters
checkpoint_count = "{circuit_data['checkpoint_count']}"
target_duration = "{circuit_data['target_duration']}"
signals_count = "{actual_signals_count}"
signals_merkle_root = "{signals_merkle_root}"
returns_merkle_root = "{COMPUTED_RETURNS_MERKLE_ROOT}"
"""

    return toml_content


def main():
    """Main function to generate and write Prover.toml."""
    # Allow specifying miner hotkey via command line
    miner_hotkey = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        toml_content = generate_prover_toml(miner_hotkey=miner_hotkey)

        with open("Prover.toml", "w") as f:
            f.write(toml_content)

        print("Successfully generated Prover.toml")

    except Exception as e:
        print(f"Error generating Prover.toml: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
