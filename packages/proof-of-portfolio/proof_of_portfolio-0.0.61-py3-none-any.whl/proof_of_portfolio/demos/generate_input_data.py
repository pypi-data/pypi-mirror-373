import json
import random
import time
import uuid
from datetime import datetime, timezone


def generate_random_data(num_miners=10, num_cps=200, num_positions=10, num_orders=5):
    """
    Generates a randomized dataset which would typically be saved as the validator_checkpoint.json file.
    """
    data = {
        "version": "6.1.0",
        "created_timestamp_ms": int(time.time() * 1000),
        "created_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "challengeperiod": {"testing": {}},
        "perf_ledgers": {},
        "positions": {},
    }

    hotkeys = [f"5{i:063d}" for i in range(num_miners)]

    # Start time for the first checkpoint, e.g., N days ago, so we have a history
    # num_cps is 200, at 2 per day, this is 100 days of data.
    start_timestamp_ms = int(time.time() * 1000) - (num_cps // 2) * 24 * 60 * 60 * 1000
    checkpoint_duration_ms = 43200000  # 12 hours

    for hotkey in hotkeys:
        # Challenge period
        data["challengeperiod"]["testing"][hotkey] = int(
            time.time() * 1000
        ) - random.randint(0, 1000000)

        # Perf ledger
        cps = []
        current_timestamp_ms = start_timestamp_ms
        for _ in range(num_cps):
            gain = random.uniform(-0.01, 0.01)
            loss = random.uniform(-0.01, 0) if gain > 0 else random.uniform(-0.01, 0.01)

            current_timestamp_ms += checkpoint_duration_ms
            cp = {
                "gain": gain,
                "loss": loss,
                "prev_ms": random.randint(1000, 100000),
                "accum_ms": checkpoint_duration_ms,
                "last_update_ms": current_timestamp_ms,
            }
            cps.append(cp)

        data["perf_ledgers"][hotkey] = {
            "cps": cps,
            "target_cp_duration_ms": checkpoint_duration_ms,
            "target_dca_duration_ms": 0,
        }

        # Positions
        positions = []
        for _ in range(num_positions):
            orders = []
            for _ in range(num_orders):
                order = {
                    "trade_pair": [random.choice(["BTC/USD", "ETH/USD", "SOL/USD"])],
                    "order_type": random.choice(["LONG", "SHORT", "FLAT"]),
                    "leverage": random.uniform(0, 1),
                    "price": random.uniform(20000, 70000),
                    "processed_ms": int(time.time() * 1000)
                    - random.randint(0, 1000000),
                    "order_uuid": str(uuid.uuid4()),
                    "bid": random.uniform(20000, 70000),
                    "ask": random.uniform(20000, 70000),
                }
                orders.append(order)

            position = {
                "position_uuid": str(uuid.uuid4()),
                "miner_hotkey": hotkey,
                "orders": orders,
                "net_leverage": random.uniform(0, 1),
                "leverage_recal_pl": random.uniform(0, 1),
                "net_worth_pl": random.uniform(0, 1),
                "open_ms": int(time.time() * 1000) - random.randint(0, 1000000),
            }
            positions.append(position)

        data["positions"][hotkey] = {"positions": positions}

    return data


def main(args):
    """
    Main function to generate the randomized data and save it to a file.
    """
    output_file = (
        args.output_file if args.output_file else "generated_validator_checkpoint.json"
    )

    print(f"Generating randomized data for {args.num_miners} miners...")
    random_data = generate_random_data(
        args.num_miners, args.num_cps, args.num_positions, args.num_orders
    )

    with open(output_file, "w") as f:
        json.dump(random_data, f, indent=2)

    print(f"Successfully generated randomized data and saved it to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a randomized validator checkpoint file."
    )
    parser.add_argument(
        "--num-miners", type=int, default=10, help="Number of miners to generate."
    )
    parser.add_argument(
        "--num-cps", type=int, default=200, help="Number of checkpoints per miner."
    )
    parser.add_argument(
        "--num-positions", type=int, default=10, help="Number of positions per miner."
    )
    parser.add_argument(
        "--num-orders", type=int, default=5, help="Number of orders per position."
    )
    parser.add_argument(
        "--output-file", type=str, help="Path to save the generated file."
    )
    args = parser.parse_args()
    main(args)
