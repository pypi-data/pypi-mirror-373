#!/usr/bin/env python3
"""
validator.py

This script processes data from data/input.json, splits it into subdirectories for each hotkey,
and scores each child by generating a Merkle tree for their data.
"""

import json
import os
import sys

from .analyze_data import split_input_json
from .miner import Miner
from . import requires_dependencies


@requires_dependencies
def score_child(hotkey_dir: str):
    """
    Scores a single child by generating a Merkle tree for their data.

    Args:
        hotkey_dir (str): Path to the child's directory

    Returns:
        dict: Score data for the child, or None if failed
    """
    # Extract hotkey from directory path
    hotkey = os.path.basename(hotkey_dir)

    # Path to the child's data.json file
    data_json_path = os.path.join(hotkey_dir, "data.json")

    if not os.path.exists(data_json_path):
        print(f"Error: Data file not found at {data_json_path}")
        return None

    # Create a Miner instance for this hotkey
    miner = Miner(hotkey, f"Miner-{hotkey[:8]}")

    # Generate tree for this child
    tree_data = miner.generate_tree(data_json_path)
    if not tree_data:
        print(f"Error: Failed to generate tree for {hotkey}")
        return None

    # Create score data
    score_data = {
        "hotkey": hotkey,
        "merkle_root": tree_data["merkle_root"],
        "actual_len": tree_data["actual_len"],
    }

    # Save score data to the child's subdirectory
    score_file = os.path.join(hotkey_dir, "score.json")
    try:
        with open(score_file, "w") as f:
            json.dump(score_data, f, indent=2)
        print(f"Score data saved to {score_file}")
    except Exception as e:
        print(f"Error saving score data: {e}")
        return None

    return score_data


@requires_dependencies
def score_all(input_json_path: str = "data/input_data.json"):
    """
    Processes input.json, splits it into subdirectories for each hotkey,
    and scores each child by generating a Merkle tree for their data.

    Args:
        input_json_path (str): Path to the input JSON file

    Returns:
        dict: Dictionary mapping hotkeys to their scores
    """
    print(f"Processing and scoring data from {input_json_path}...")

    # Split input.json into subdirectories
    children_count = split_input_json(input_json_path)
    if children_count == 0:
        print("No children to score.")
        return {}

    # Get all child directories
    children_dir = os.path.join(os.path.dirname(input_json_path), "children")
    child_dirs = [
        os.path.join(children_dir, d)
        for d in os.listdir(children_dir)
        if os.path.isdir(os.path.join(children_dir, d))
    ]

    # Score each child
    scores = {}
    for child_dir in child_dirs:
        hotkey = os.path.basename(child_dir)
        print(f"\nScoring child: {hotkey}")

        score_data = score_child(child_dir)
        if score_data:
            scores[hotkey] = score_data

    # Save all scores to a summary file
    summary_file = os.path.join(os.path.dirname(input_json_path), "scores_summary.json")
    try:
        with open(summary_file, "w") as f:
            json.dump(scores, f, indent=2)
        print(f"\nAll scores saved to {summary_file}")
    except Exception as e:
        print(f"Error saving scores summary: {e}")

    print(f"Successfully scored {len(scores)} children.")
    return scores


def main():
    # Process command line arguments
    input_json_path = "../data/input_data.json"
    if len(sys.argv) > 1:
        input_json_path = sys.argv[1]

    # Score all children
    scores = score_all(input_json_path)

    # Print summary
    print("\nScoring Summary:")
    for hotkey, score_data in scores.items():
        print(f"Hotkey: {hotkey[:8]}... - Signals: {score_data['actual_len']}")


if __name__ == "__main__":
    main()
