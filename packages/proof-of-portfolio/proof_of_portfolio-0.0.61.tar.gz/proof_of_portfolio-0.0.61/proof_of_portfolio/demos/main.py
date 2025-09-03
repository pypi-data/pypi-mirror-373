import json

from ..proof_generator import generate_proof


def main(args):
    """Demo main function - loads data from file and calls core proof generation logic."""
    hotkey = args.hotkey
    print("Loading data from validator_checkpoint.json...")
    with open("validator_checkpoint.json", "r") as f:
        data = json.load(f)

    if hotkey and hotkey not in data["perf_ledgers"]:
        print(f"Error: Hotkey '{hotkey}' not found in validator checkpoint data.")
        print(f"Available hotkeys: {list(data['perf_ledgers'].keys())}")
        return 1

    result = generate_proof(data, hotkey, True)
    return 0 if result and result.get("proof_results", {}).get("proof_generated") else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a zero-knowledge proof for a miner's portfolio data."
    )
    parser.add_argument(
        "--hotkey",
        type=str,
        help="The hotkey of the miner to generate a proof for. If not provided, uses the first available miner.",
    )

    args = parser.parse_args()
    exit_code = main(args)
    exit(exit_code)
