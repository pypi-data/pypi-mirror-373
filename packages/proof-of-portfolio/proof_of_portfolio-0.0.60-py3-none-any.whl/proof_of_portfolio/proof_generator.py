import subprocess
import toml
import re
import os
import time
import math
import bittensor as bt

# Constants for the circuit
MAX_CHECKPOINTS = 200
MAX_SIGNALS = 256
MERKLE_DEPTH = 8
ARRAY_SIZE = 256
SCALING_FACTOR = 10**9
MAX_DAYS = 120


def run_command(command, cwd, verbose=True):
    """Executes a command in a given directory and returns the output."""
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        if verbose:
            bt.logging.error("Error:")
            bt.logging.error(result.stdout)
            bt.logging.error(result.stderr)
        raise RuntimeError(
            f"Command {' '.join(command)} failed with exit code {result.returncode}"
        )
    return result.stdout


def parse_nargo_struct_output(output):
    """
    Parses the raw output of a nargo execute command that returns a struct.
    """
    if (
        "[" in output
        and "]" in output
        and not ("MerkleTree" in output or "ReturnsData" in output)
    ):
        array_matches = re.findall(r"\[([^\]]+)\]", output)
        if array_matches:
            array_content = array_matches[-1]
            values = []
            for item in array_content.split(","):
                item = item.strip()
                if item.startswith("0x"):
                    try:
                        values.append(str(int(item, 16)))
                    except ValueError:
                        continue
                elif item.lstrip("-").isdigit():
                    values.append(item)
            if values:
                return values

    struct_start = output.find("{")
    struct_end = output.rfind("}")

    if struct_start == -1 or struct_end == -1:
        return re.findall(r"Field\(([-0-9]+)\)", output)

    struct_content = output[struct_start : struct_end + 1]

    if "MerkleTree" in output:
        tree = {}
        try:
            # Parse leaf_hashes
            if "leaf_hashes:" in struct_content:
                start = struct_content.find("leaf_hashes:") + len("leaf_hashes:")
                end = struct_content.find(", path_elements:")
                leaf_section = struct_content[start:end].strip()
                if leaf_section.startswith("[") and leaf_section.endswith("]"):
                    leaf_content = leaf_section[1:-1]
                    tree["leaf_hashes"] = [
                        x.strip() for x in leaf_content.split(",") if x.strip()
                    ]

            # Parse path_elements
            if "path_elements:" in struct_content:
                start = struct_content.find("path_elements:") + len("path_elements:")
                end = struct_content.find(", path_indices:")
                path_elem_section = struct_content[start:end].strip()
                tree["path_elements"] = parse_nested_arrays(path_elem_section)

            # Parse path_indices
            if "path_indices:" in struct_content:
                start = struct_content.find("path_indices:") + len("path_indices:")
                end = struct_content.find(", root:")
                path_idx_section = struct_content[start:end].strip()
                tree["path_indices"] = parse_nested_arrays(path_idx_section)

            # Parse root
            if "root:" in struct_content:
                start = struct_content.find("root:") + len("root:")
                root_section = struct_content[start:].strip().rstrip("}")
                tree["root"] = root_section.strip()

            return tree
        except Exception:
            pass

    values = []

    parts = re.split(r"[,\s]+", struct_content)
    for part in parts:
        part = part.strip("{}[](), \t\n\r")
        if not part:
            continue

        # Check if it's a hex value
        if part.startswith("0x") and len(part) > 2:
            try:
                values.append(str(int(part, 16)))
                continue
            except ValueError:
                pass

        # Check if it's a negative number
        if part.lstrip("-").isdigit():
            values.append(part)

    return values


def parse_nested_arrays(section):
    """Helper function to parse nested array structures like [[...], [...]]"""
    if not section.strip().startswith("["):
        return []

    arrays = []
    depth = 0
    current_array = ""

    for char in section:
        if char == "[":
            depth += 1
            if depth == 2:  # Start of inner array
                current_array = ""
            elif depth == 1:  # Start of outer array
                continue
        elif char == "]":
            depth -= 1
            if depth == 1:  # End of inner array
                if current_array.strip():
                    arrays.append(
                        [x.strip() for x in current_array.split(",") if x.strip()]
                    )
                current_array = ""
            elif depth == 0:  # End of outer array
                break
        elif depth == 2:  # Inside inner array
            current_array += char

    return arrays


def parse_single_field_output(output):
    """
    Parses nargo output that contains a single field value.
    Handles both new hex format (0x...) and old Field() format.
    Returns the integer value, or None if no field found.
    """
    if "0x" in output:
        hex_match = output.split("0x")[1].split()[0]
        return int(hex_match, 16)

    if "Field(" in output:
        return int(output.split("Field(")[1].split(")")[0])

    return None


def field_to_toml_value(f):
    """Converts a negative integer field to a proper field element string."""
    PRIME = (
        21888242871839275222246405745257275088548364400416034343698204186575808495617
    )
    if f < 0:
        return str(f + PRIME)
    return str(f)


def run_bb_prove(circuit_dir):
    """
    Runs barretenberg proving.
    Returns proof generation time and status.
    """
    print("\n--- Running Barretenberg Proof Generation ---")

    try:
        subprocess.run(["bb", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "Error: bb (Barretenberg) not found. Please install it using \n`curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/master/barretenberg/cpp/installation/install | bash`"
        )
        return None, False

    try:
        target_dir = os.path.join(circuit_dir, "target")
        proof_dir = os.path.join(circuit_dir, "proof")
        vk_dir = os.path.join(circuit_dir, "vk")

        os.makedirs(proof_dir, exist_ok=True)
        os.makedirs(vk_dir, exist_ok=True)

        witness_file = os.path.join(target_dir, "witness.gz")
        circuit_file = os.path.join(target_dir, "circuits.json")

        proof_file = proof_dir

        prove_start = time.time()
        prove_result = subprocess.run(
            ["bb", "prove", "-b", circuit_file, "-w", witness_file, "-o", proof_file],
            capture_output=True,
            text=True,
            cwd=circuit_dir,
        )
        prove_time = time.time() - prove_start

        if prove_result.returncode != 0:
            print("bb prove failed:")
            print(
                " ".join(
                    [
                        "bb",
                        "prove",
                        "-b",
                        circuit_file,
                        "-w",
                        witness_file,
                        "-o",
                        proof_file,
                    ]
                )
            )
            print(prove_result.stdout)
            print(prove_result.stderr)
            return None, False

        print(f"Proof generated in {prove_time:.3f}s")
        return prove_time, True

    except Exception as e:
        print(f"Error during proof generation/verification: {e}")
        return None, False


def aggregate_daily_returns(cps, target_duration, daily_checkpoints=2):
    """
    Aggregate checkpoint returns into daily returns following subnet's daily_return_log logic.
    Only includes complete days with proper checkpoint accumulation.

    Args:
        cps: List of checkpoint dictionaries
        target_duration: Target checkpoint duration in ms
        daily_checkpoints: Number of checkpoints expected per day (from ValiConfig.DAILY_CHECKPOINTS)
    """
    from datetime import datetime, timezone

    if not cps:
        return []

    TARGET_CHECKPOINT_DURATION_MS = target_duration

    daily_groups = {}

    for cp in cps:
        start_time = cp["last_update_ms"] - cp["accum_ms"]
        full_cell = cp["accum_ms"] == TARGET_CHECKPOINT_DURATION_MS

        running_date = datetime.fromtimestamp(start_time / 1000, tz=timezone.utc).date()

        if full_cell:
            if running_date not in daily_groups:
                daily_groups[running_date] = []
            daily_groups[running_date].append(cp)

    daily_returns = []
    for running_date, day_checkpoints in sorted(daily_groups.items()):
        if len(day_checkpoints) == daily_checkpoints:
            daily_return = sum(cp["gain"] + cp["loss"] for cp in day_checkpoints)
            daily_returns.append(daily_return)

    return daily_returns


def generate_proof(
    data=None,
    miner_hotkey=None,
    verbose=None,
    annual_risk_free_percentage=4.19,
    use_weighting=False,
    bypass_confidence=False,
    daily_checkpoints=2,
    witness_only=False,
):
    """
    Core proof generation logic.

    Args:
        data: Optional dictionary containing perf_ledgers and positions.
              If None, will read from validator_checkpoint.json
        miner_hotkey: The hotkey of the miner to generate proof for.
                     If None and reading from file, uses first available hotkey
        verbose: Optional boolean to control logging verbosity.
                If None, auto-detects (demo mode = verbose, production = minimal)
        annual_risk_free_percentage: Annual risk-free rate percentage (default 4.19)
        use_weighting: Whether to use weighted calculations (default False)
        bypass_confidence: Whether to bypass confidence thresholds (default False)
        daily_checkpoints: Number of checkpoints expected per day (default 2)
        witness_only: If True, skip barretenberg proof generation for faster testing (default False)

    Returns:
        Dictionary with proof results including status, portfolio_metrics, etc.
    """
    bt.logging.info(
        f"generate_proof called with verbose={verbose}, miner_hotkey={miner_hotkey[:8] if miner_hotkey else None}"
    )

    # Auto-detect mode: demo mode if reading from file, production if data provided
    is_demo_mode = data is None
    if verbose is None:
        verbose = is_demo_mode

    bt.logging.info(
        f"After auto-detect: verbose={verbose}, is_demo_mode={is_demo_mode}"
    )

    try:
        if data is None:
            if verbose:
                bt.logging.info("Loading data from validator_checkpoint.json...")
        import json

        with open("validator_checkpoint.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        bt.logging.error(f"Failed to load data {e}")

    if miner_hotkey is None:
        miner_hotkey = list(data["perf_ledgers"].keys())[0]
        if verbose:
            bt.logging.info(
                f"No hotkey specified, using first available: {miner_hotkey}"
            )
    else:
        if verbose:
            bt.logging.info(f"Using specified hotkey: {miner_hotkey}")

    if miner_hotkey not in data["perf_ledgers"]:
        raise ValueError(
            f"Hotkey '{miner_hotkey}' not found in data. Available: {list(data['perf_ledgers'].keys())}"
        )

    perf_ledger = data["perf_ledgers"][miner_hotkey]
    positions = data["positions"][miner_hotkey]["positions"]
    if verbose:
        bt.logging.info("Preparing circuit inputs...")

    cps = perf_ledger["cps"]
    if len(cps) > MAX_CHECKPOINTS:
        if verbose:
            bt.logging.warning(
                f"Warning: Miner has {len(cps)} checkpoints, but circuit only supports {MAX_CHECKPOINTS}. Truncating."
            )
        cps = cps[:MAX_CHECKPOINTS]

    target_duration = perf_ledger["target_cp_duration_ms"]

    gains = [int(c["gain"] * SCALING_FACTOR) for c in cps]
    losses = [int(c["loss"] * SCALING_FACTOR) for c in cps]
    last_update_times = [c["last_update_ms"] for c in cps]
    accum_times = [c["accum_ms"] for c in cps]
    checkpoint_count = len(cps)

    gains += [0] * (MAX_CHECKPOINTS - len(gains))
    losses += [0] * (MAX_CHECKPOINTS - len(losses))
    last_update_times += [0] * (MAX_CHECKPOINTS - len(last_update_times))
    accum_times += [0] * (MAX_CHECKPOINTS - len(accum_times))

    daily_log_returns = aggregate_daily_returns(cps, target_duration, daily_checkpoints)
    aggregated_gains = []
    aggregated_losses = []
    aggregated_last_update_times = []
    aggregated_accum_times = []

    for i, daily_return in enumerate(daily_log_returns):
        if daily_return >= 0:
            aggregated_gains.append(int(daily_return * SCALING_FACTOR))
            aggregated_losses.append(0)
        else:
            aggregated_gains.append(0)
            aggregated_losses.append(int(daily_return * SCALING_FACTOR))

        aggregated_last_update_times.append(target_duration + (i * target_duration))
        aggregated_accum_times.append(target_duration)

    aggregated_checkpoint_count = len(daily_log_returns)

    aggregated_gains += [0] * (MAX_CHECKPOINTS - len(aggregated_gains))
    aggregated_losses += [0] * (MAX_CHECKPOINTS - len(aggregated_losses))
    aggregated_last_update_times += [0] * (
        MAX_CHECKPOINTS - len(aggregated_last_update_times)
    )
    aggregated_accum_times += [0] * (MAX_CHECKPOINTS - len(aggregated_accum_times))

    if verbose:
        bt.logging.info(
            f"Processing {checkpoint_count} raw checkpoints for merkle roots"
        )
        bt.logging.info(
            f"Using {aggregated_checkpoint_count} aggregated daily returns for metrics"
        )

    all_orders = []
    for pos in positions:
        all_orders.extend(pos["orders"])

    signals_count = len(all_orders)
    if signals_count > MAX_SIGNALS:
        if verbose:
            bt.logging.warning(
                f"Warning: Miner has {signals_count} signals, but circuit only supports {MAX_SIGNALS}. Truncating."
            )
        all_orders = all_orders[:MAX_SIGNALS]
        signals_count = MAX_SIGNALS

    trade_pair_map = {}
    trade_pair_counter = 0

    signals = []
    for order in all_orders:
        trade_pair_str = order.get("trade_pair", ["UNKNOWN"])[0]
        if trade_pair_str not in trade_pair_map:
            trade_pair_map[trade_pair_str] = trade_pair_counter
            trade_pair_counter += 1

        order_type_str = order["order_type"]
        order_type_map = {"SHORT": 2, "LONG": 1, "FLAT": 0}
        price = int(order.get("price", 0) * SCALING_FACTOR)
        order_uuid = order.get("order_uuid", "0")
        bid = int(order.get("bid", 0) * SCALING_FACTOR)
        ask = int(order.get("ask", 0) * SCALING_FACTOR)
        processed_ms = order.get("processed_ms", 0)

        signals.append(
            {
                "trade_pair": str(trade_pair_map[trade_pair_str]),
                "order_type": str(order_type_map.get(order_type_str, 0)),
                "leverage": str(int(abs(order.get("leverage", 0)) * SCALING_FACTOR)),
                "price": str(price),
                "processed_ms": str(processed_ms),
                "order_uuid": f"0x{order_uuid.replace('-', '')}",
                "bid": str(bid),
                "ask": str(ask),
            }
        )

    # Pad signals too
    signals += [
        {
            "trade_pair": "0",
            "order_type": "0",
            "leverage": "0",
            "price": "0",
            "processed_ms": "0",
            "order_uuid": "0x0",
            "bid": "0",
            "ask": "0",
        }
    ] * (MAX_SIGNALS - len(signals))

    if verbose:
        bt.logging.info(
            f"Prepared {aggregated_checkpoint_count} aggregated daily returns and {signals_count} signals for circuit."
        )

    if verbose:
        bt.logging.info("Running tree_generator circuit...")
    else:
        bt.logging.info(f"Generating tree for hotkey {miner_hotkey}...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tree_generator_dir = os.path.join(current_dir, "tree_generator")

    tree_prover_input = {"signals": signals, "actual_len": str(signals_count)}
    os.makedirs(tree_generator_dir, exist_ok=True)
    with open(os.path.join(tree_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(tree_prover_input, f)

    output = run_command(
        ["nargo", "execute", "--silence-warnings" if not verbose else ""],
        tree_generator_dir,
        verbose,
    )

    tree = parse_nargo_struct_output(output)
    try:
        path_elements = tree["path_elements"]
        path_indices = tree["path_indices"]
        signals_merkle_root = tree["root"]
    except Exception:
        raise RuntimeError(
            "Unexpected tree_generator output structure, expected MerkleTree dict with leaf_hashes, path_elements, path_indices, and root"
        )

    if verbose:
        print(f"Generated signals Merkle root: {signals_merkle_root}")
        if isinstance(signals_merkle_root, str) and signals_merkle_root.startswith(
            "0x"
        ):
            print(f"Signals Merkle root (hex): {signals_merkle_root}")
        else:
            print(f"Signals Merkle root (int): {signals_merkle_root}")

    # This one is similar to tree gen but is the validator's contribution to the circuit (cps)
    if verbose:
        print("Running returns_generator circuit...")
    else:
        print(f"Generating returns for hotkey {miner_hotkey}...")
    returns_generator_dir = os.path.join(current_dir, "returns_generator")

    returns_prover_input = {
        "gains": [str(g) for g in aggregated_gains],
        "losses": [str(l) for l in aggregated_losses],
        "last_update_times": [str(t) for t in aggregated_last_update_times],
        "accum_times": [str(a) for a in aggregated_accum_times],
        "checkpoint_count": str(aggregated_checkpoint_count),
        "target_duration": str(target_duration),
    }

    os.makedirs(returns_generator_dir, exist_ok=True)
    with open(os.path.join(returns_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(returns_prover_input, f)

    output = run_command(
        ["nargo", "execute", "--silence-warnings"], returns_generator_dir, verbose
    )

    fields = parse_nargo_struct_output(output)

    # Parse the ReturnsData struct: log_returns array + returns_merkle_root + valid_days
    if len(fields) >= 2:
        # Last field is valid_days, second to last is returns_merkle_root
        valid_days = fields[-1]
        returns_merkle_root = fields[-2]
    else:
        # Fallback for unexpected format
        num_log_returns = MAX_DAYS
        returns_merkle_root = (
            fields[num_log_returns] if len(fields) > num_log_returns else fields[-2]
        )
        valid_days = fields[-1]

    if verbose:
        print(f"Generated returns Merkle root: {returns_merkle_root}")
        print(
            f"Returns Merkle root (hex): 0x{hex(int(returns_merkle_root))[2:].zfill(64)}"
        )
        print(f"Number of valid daily returns: {valid_days}")

    if verbose:
        print("Running main proof of portfolio circuit...")
    else:
        print(f"Generating witness for hotkey {miner_hotkey}...")
    main_circuit_dir = os.path.join(current_dir, "circuits")

    # Convert risk-free rate to daily log rate and scale for circuit
    annual_risk_free_decimal = annual_risk_free_percentage / 100
    daily_log_risk_free_rate = math.log(1 + annual_risk_free_decimal) / 365
    risk_free_rate_scaled = int(daily_log_risk_free_rate * SCALING_FACTOR)

    # Finally, LFG
    main_prover_input = {
        "gains": [str(g) for g in aggregated_gains],
        "losses": [str(l) for l in aggregated_losses],
        "last_update_times": [str(t) for t in aggregated_last_update_times],
        "accum_times": [str(a) for a in aggregated_accum_times],
        "checkpoint_count": str(aggregated_checkpoint_count),
        "target_duration": str(target_duration),
        "signals": signals,
        "signals_count": str(signals_count),
        "path_elements": [
            [
                field_to_toml_value(
                    int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                )
                for x in p
            ]
            for p in path_elements
        ],
        "path_indices": [
            [
                int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
                for x in p
            ]
            for p in path_indices
        ],
        "signals_merkle_root": (
            signals_merkle_root
            if isinstance(signals_merkle_root, str)
            else str(signals_merkle_root)
        ),
        "returns_merkle_root": field_to_toml_value(int(returns_merkle_root)),
        "risk_free_rate": str(risk_free_rate_scaled),
        "use_weighting": str(int(use_weighting)),
        "bypass_confidence": str(int(bypass_confidence)),
    }

    os.makedirs(main_circuit_dir, exist_ok=True)
    with open(os.path.join(main_circuit_dir, "Prover.toml"), "w") as f:
        toml.dump(main_prover_input, f)

    if verbose:
        print("Executing main circuit to generate witness...")
    witness_start = time.time()
    output = run_command(
        ["nargo", "execute", "witness", "--silence-warnings"], main_circuit_dir, verbose
    )
    witness_time = time.time() - witness_start
    if verbose:
        print(f"Witness generation completed in {witness_time:.3f}s")

    fields = parse_nargo_struct_output(output)
    if len(fields) < 7:
        raise RuntimeError(
            f"Expected 7 output fields from main circuit, got {len(fields)}: {fields}"
        )

    avg_daily_pnl_raw = fields[0]
    sharpe_raw = fields[1]
    drawdown_raw = fields[2]
    calmar_raw = fields[3]
    omega_raw = fields[4]
    sortino_raw = fields[5]
    stat_confidence_raw = fields[6]

    def field_to_signed_int(field_str):
        if isinstance(field_str, str) and field_str.startswith("0x"):
            val = int(field_str, 16)
        else:
            val = int(field_str)

        # Noir's i64 as u64 casting uses standard two's complement
        # Convert from u64 back to i64 using two's complement
        if val >= 2**63:  # If the high bit is set, it's negative
            return val - 2**64  # Convert from unsigned to signed
        else:
            return val  # Positive values unchanged

    if verbose:
        print("Raw field values before conversion:")
        print(f"  avg_daily_pnl_raw: {avg_daily_pnl_raw}")
        print(f"  sharpe_raw: {sharpe_raw}")
        print(f"  drawdown_raw: {drawdown_raw}")

    avg_daily_pnl_value = field_to_signed_int(avg_daily_pnl_raw)
    sharpe_ratio_raw = field_to_signed_int(sharpe_raw)
    max_drawdown_raw = field_to_signed_int(drawdown_raw)
    calmar_ratio_raw = field_to_signed_int(calmar_raw)
    omega_ratio_raw = field_to_signed_int(omega_raw)
    sortino_ratio_raw = field_to_signed_int(sortino_raw)
    stat_confidence_raw = field_to_signed_int(stat_confidence_raw)

    if verbose:
        print("Converted values:")
        print(f"  avg_daily_pnl_value: {avg_daily_pnl_value}")
        print(f"  sharpe_ratio_raw: {sharpe_ratio_raw}")
        print(f"  max_drawdown_raw: {max_drawdown_raw}")

    avg_daily_pnl_scaled = avg_daily_pnl_value / SCALING_FACTOR
    sharpe_ratio_scaled = sharpe_ratio_raw / SCALING_FACTOR
    max_drawdown_scaled = max_drawdown_raw / SCALING_FACTOR
    calmar_ratio_scaled = calmar_ratio_raw / SCALING_FACTOR
    omega_ratio_scaled = omega_ratio_raw / SCALING_FACTOR
    sortino_ratio_scaled = sortino_ratio_raw / SCALING_FACTOR
    stat_confidence_scaled = stat_confidence_raw / SCALING_FACTOR

    if witness_only:
        prove_time, verification_success = None, False
        if verbose:
            print("Skipping barretenberg proof generation (witness_only=True)")
    else:
        prove_time, verification_success = run_bb_prove(main_circuit_dir)

    # Always print key production info: hotkey and verification status
    print(f"Hotkey: {miner_hotkey}")
    print(f"Orders processed: {signals_count}")
    print(f"Signals Merkle Root: {signals_merkle_root}")
    print(f"Returns Merkle Root: {returns_merkle_root}")
    print(f"Average Daily PnL: {avg_daily_pnl_scaled:.9f}")
    print(f"Sharpe Ratio: {sharpe_ratio_scaled:.9f}")
    print(f"Max Drawdown: {max_drawdown_scaled:.9f} ({max_drawdown_scaled * 100:.6f}%)")
    print(f"Calmar Ratio: {calmar_ratio_scaled:.9f}")
    print(f"Omega Ratio: {omega_ratio_scaled:.9f}")
    print(f"Sortino Ratio: {sortino_ratio_scaled:.9f}")
    print(f"Statistical Confidence: {stat_confidence_scaled:.9f}")

    if prove_time is not None:
        print(f"Proof generated in {prove_time}s")
    else:
        print("Proof generation failed")

    if verbose:
        print("\n--- Proof Generation Complete ---")
        print("\n=== MERKLE ROOTS ===")
        print(f"Signals Merkle Root: {signals_merkle_root}")
        print(f"Returns Merkle Root: {returns_merkle_root}")

        print("\n=== DATA SUMMARY ===")
        print(f"Daily returns processed: {aggregated_checkpoint_count}")
        print(f"Trading signals processed: {signals_count}")
        print(f"Valid daily returns: {valid_days}")

        print("\n=== PROOF GENERATION RESULTS ===")
        print(f"Witness generation time: {witness_time:.3f}s")
        if prove_time is not None:
            print(f"Proof generation time: {prove_time:.3f}s")
            print(
                f"Proof verification: {'✅ PASSED' if verification_success else '❌ FAILED'}"
            )
        else:
            print("Unable to prove or verify due to an error.")

    # Return structured results for programmatic access
    return {
        "merkle_roots": {
            "signals": signals_merkle_root,
            "returns": returns_merkle_root,
        },
        "portfolio_metrics": {
            "avg_daily_pnl_raw": avg_daily_pnl_value,
            "avg_daily_pnl_scaled": avg_daily_pnl_scaled,
            "sharpe_ratio_raw": sharpe_ratio_raw,
            "sharpe_ratio_scaled": sharpe_ratio_scaled,
            "max_drawdown_raw": max_drawdown_raw,
            "max_drawdown_scaled": max_drawdown_scaled,
            "max_drawdown_percentage": max_drawdown_scaled * 100,
            "calmar_ratio_raw": calmar_ratio_raw,
            "calmar_ratio_scaled": calmar_ratio_scaled,
            "omega_ratio_raw": omega_ratio_raw,
            "omega_ratio_scaled": omega_ratio_scaled,
            "sortino_ratio_raw": sortino_ratio_raw,
            "sortino_ratio_scaled": sortino_ratio_scaled,
            "stat_confidence_raw": stat_confidence_raw,
            "stat_confidence_scaled": stat_confidence_scaled,
        },
        "data_summary": {
            "daily_returns_processed": aggregated_checkpoint_count,
            "signals_processed": signals_count,
            "valid_daily_returns": int(valid_days),
        },
        "proof_results": {
            "witness_generation_time": witness_time,
            "proof_generation_time": prove_time,
            "verification_success": verification_success,
            "proof_generated": prove_time is not None,
        },
    }
