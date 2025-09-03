import json
import subprocess
from datetime import datetime, timezone, date

SCALE = 10_000_000
DAILY_CHECKPOINTS = 2


class LedgerUtils:
    @staticmethod
    def daily_return_log_by_date(
        checkpoints: list, target_duration: int
    ) -> dict[date, float]:
        if not checkpoints:
            return {}

        daily_groups = {}
        n_checkpoints_per_day = DAILY_CHECKPOINTS

        for cp in checkpoints:
            start_time = cp["last_update_ms"] - cp["accum_ms"]
            full_cell = cp["accum_ms"] == target_duration

            running_date = datetime.fromtimestamp(
                start_time / 1000, tz=timezone.utc
            ).date()

            if full_cell:
                if running_date not in daily_groups:
                    daily_groups[running_date] = []
                daily_groups[running_date].append(cp)

        date_return_map = {}
        for running_date, day_checkpoints in sorted(daily_groups.items()):
            if len(day_checkpoints) == n_checkpoints_per_day:
                daily_return = sum(cp["gain"] + cp["loss"] for cp in day_checkpoints)
                date_return_map[running_date] = daily_return

        return date_return_map

    @staticmethod
    def daily_return_log(checkpoints: list, target_duration: int) -> list[float]:
        date_return_map = LedgerUtils.daily_return_log_by_date(
            checkpoints, target_duration
        )
        return list(date_return_map.values())


def load_validator_checkpoint_data(filepath: str = "validator_checkpoint.json"):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Validator checkpoint file not found at {filepath}")
        return None


def extract_test_data(
    validator_data: dict, miner_id: str = None, max_checkpoints: int = 200
):
    if not validator_data or "perf_ledgers" not in validator_data:
        print("No perf_ledgers found in validator data")
        return None

    perf_ledgers = validator_data["perf_ledgers"]

    if miner_id:
        if miner_id not in perf_ledgers:
            print(f"Miner {miner_id} not found in validator data")
            return None
        miner_data = perf_ledgers[miner_id]
    else:
        miner_ids = list(perf_ledgers.keys())
        if not miner_ids:
            print("No miners found in validator data")
            return None
        miner_id = miner_ids[0]
        miner_data = perf_ledgers[miner_id]
        print(f"Using first miner: {miner_id}")

    checkpoints = miner_data.get("cps", [])
    target_duration = miner_data.get("target_cp_duration_ms", 43200000)

    if not checkpoints:
        print(f"No checkpoints found for miner {miner_id}")
        return None

    test_checkpoints = checkpoints[:max_checkpoints]

    gains = [int(cp["gain"] * SCALE) for cp in test_checkpoints]
    losses = [int(cp["loss"] * SCALE) for cp in test_checkpoints]
    last_update_times = [cp["last_update_ms"] for cp in test_checkpoints]
    accum_times = [cp["accum_ms"] for cp in test_checkpoints]

    while len(gains) < max_checkpoints:
        gains.append(0)
        losses.append(0)
        last_update_times.append(0)
        accum_times.append(0)

    return {
        "gains": gains,
        "losses": losses,
        "last_update_times": last_update_times,
        "accum_times": accum_times,
        "checkpoint_count": len(test_checkpoints),
        "test_checkpoints": test_checkpoints,
        "target_duration": target_duration,
        "miner_id": miner_id,
    }


def run_nargo(
    gains: list,
    losses: list,
    last_update_times: list,
    accum_times: list,
    checkpoint_count: int,
    target_duration: int,
    prover_path: str,
    output_format: str = "tuple",
):
    with open(prover_path, "w") as f:
        f.write(f'checkpoint_count = "{checkpoint_count}"\n')
        f.write(f"gains = {gains}\n")
        f.write(f"losses = {losses}\n")
        f.write(f"last_update_times = {last_update_times}\n")
        f.write(f"accum_times = {accum_times}\n")
        f.write(f'target_duration = "{target_duration}"\n')

    result = subprocess.run(
        ["nargo", "execute"],
        capture_output=True,
        text=True,
        cwd=prover_path.rsplit("/", 1)[0],
    )

    if result.returncode != 0:
        print("Nargo execute failed:")
        print(result.stderr)
        raise RuntimeError("nargo execute failed")

    if "Circuit output:" in result.stdout:
        output_line = result.stdout.split("Circuit output: ")[1].strip()

        try:
            if output_format == "tuple":
                if output_line.startswith("Vec([Vec([") and output_line.endswith("])"):
                    # Find the end of the inner Vec array
                    inner_vec_end = output_line.rfind("]), Field(")
                    if inner_vec_end != -1:
                        array_part = output_line[
                            10:inner_vec_end
                        ]  # Remove 'Vec([Vec([' at start
                        count_part = output_line[
                            inner_vec_end + 9 : -2
                        ]  # Get number after '), Field(' and before '])'

                        # Remove parentheses from count part if present
                        if count_part.startswith("(") and count_part.endswith(")"):
                            count_part = count_part[1:-1]

                        valid_days = int(count_part)

                        field_values = []
                        if array_part:
                            field_strings = array_part.split(", ")
                            for field_str in field_strings:
                                if field_str.startswith(
                                    "Field("
                                ) and field_str.endswith(")"):
                                    val = int(field_str[6:-1])
                                    if val >= 2**63:
                                        val = val - 2**64
                                    field_values.append(val / SCALE)
                                else:
                                    field_values.append(0.0)

                        return field_values[:valid_days], valid_days
            elif output_format == "flat_vec":
                import re

                str_numbers = re.findall(r"Field\((.*?)\)", output_line)
                all_returns = []
                for s_num in str_numbers:
                    unsigned_i = int(s_num, 0)  # Handles hex and decimal
                    if unsigned_i >= 2**63:
                        i = unsigned_i - 2**64
                    else:
                        i = unsigned_i
                    all_returns.append(float(i) / SCALE)
                return all_returns, len(all_returns)

        except (ValueError, IndexError) as e:
            print(f"Error parsing circuit output: {e}")
            print(f"Raw output: {output_line}")

    return [], 0
