#!/usr/bin/env python3
"""
Proof of Portfolio (pop) CLI

A command-line interface for the Proof of Portfolio system.

This CLI provides commands for both Miners and Validators.

Miner Commands:
  - generate-tree: Generate a Merkle tree for a miner's portfolio data.

Validator Commands:
  - validate: Validate a single miner's data and generate their Merkle tree.
  - validate-all: Validate all miners' data from an input file or directory.
  - analyse-data: Pre-process a large data file, splitting it by miner.

Utility Commands:
  - generate-test-data: Create a randomized test data file for validation.
  - save-tree: Save a generated Merkle tree to a specified output file.
  - demo: Run demonstration scripts for various system components.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Tuple, Optional

from .miner import Miner
from .validator import score_child, score_all
from .analyze_data import split_input_json
from .demos import (
    log_returns as demo_log_returns,
    sharpe as demo_sharpe,
    omega as demo_omega,
    sortino as demo_sortino,
    calmar as demo_calmar,
    tstat as demo_tstat,
    all as demo_all,
    drawdown as demo_drawdown,
    main as demo_main,
    generate_input_data,
)


def _handle_data_file_path(
    data_file_path: Optional[str],
) -> Tuple[Optional[Path], Optional[Path]]:
    """Handles path logic for finding data.json."""
    if not data_file_path:
        print(
            "Warning: --path parameter was omitted, please provide a path to the data.json file."
        )
        return None, None

    path = Path(data_file_path)

    if not path.exists():
        print(f"Error: Path not found at {path}")
        return None, None

    if path.is_dir():
        data_file = path / "data.json"
        parent_dir = path
    else:
        data_file = path
        parent_dir = path.parent

    if not data_file.exists():
        print(f"Error: Data file not found at {data_file}")
        return None, None

    return data_file, parent_dir


def _handle_tree_file_path(
    path_str: Optional[str],
) -> Tuple[Optional[Path], Optional[str]]:
    """Handles path logic for finding tree.json and determining hotkey."""
    if not path_str:
        print(
            "Warning: --path parameter was omitted, please provide a path to the tree.json file or hotkey directory."
        )
        return None, None

    path = Path(path_str)

    if not path.exists():
        print(f"Error: Path not found: {path}")
        return None, None

    if path.is_file():
        tree_file = path
        hotkey = path.parent.name
    else:
        tree_file = path / "tree.json"
        hotkey = path.name

    if not tree_file.exists():
        print(f"Error: Tree file not found at {tree_file}")
        return None, None

    return tree_file, hotkey


def generate_tree(args):
    """
    Generate a merkle tree for a miner using their data.json file.

    Args:
        args: Command line arguments containing the data_file path, hotkey, and output_path
    """
    try:
        data_file, parent_dir = _handle_data_file_path(getattr(args, "data_file", None))
        if not data_file or not parent_dir:
            return 1

        # If hotkey is not provided, try to extract it from the parent directory name
        hotkey = args.hotkey
        if not hotkey:
            if parent_dir.name != "." and parent_dir.name != "":
                hotkey = parent_dir.name
            else:
                print(
                    "Error: Hotkey not provided and could not be determined from directory structure."
                )
                print("Please provide a hotkey using the --hotkey option.")
                return 1

        print(f"Generating merkle tree for miner {hotkey} using data from {data_file}")

        # Create a Miner instance
        miner = Miner(hotkey, f"Miner-{hotkey[:8] if len(hotkey) > 8 else hotkey}")

        # Generate the tree with optional output path
        output_path = (
            args.output_path
            if hasattr(args, "output_path") and args.output_path
            else None
        )
        if output_path is None:
            print(
                "Note: --output parameter was omitted, tree will be saved in the same directory as the data file."
            )

        tree_data = miner.generate_tree(str(data_file), output_path)

        if not tree_data:
            print(f"Error: Failed to generate tree for {hotkey}")
            return 1

        print(f"Successfully generated merkle tree for {hotkey}")

        # Generate score
        parent_dir = data_file.parent
        score_data = score_child(str(parent_dir))

        if score_data:
            print(f"Score data saved to {parent_dir / 'score.json'}")
            print(f"Merkle root: {score_data['merkle_root']}")
            print(f"Actual length: {score_data['actual_len']}")

        return 0
    except Exception as e:
        print(f"Error generating tree: {str(e)}")
        return 1


def validate_miner(args):
    """
    Generate a merkle tree for a miner as a validator.

    Args:
        args: Command line arguments containing the data_file path
    """
    try:
        data_file, parent_dir = _handle_data_file_path(getattr(args, "data_file", None))
        if not data_file or not parent_dir:
            return 1

        print(f"Validating miner using data from {data_file}")

        # Score the child
        score_data = score_child(str(parent_dir))

        if not score_data:
            print("Error: Failed to validate miner")
            return 1

        print("Successfully validated miner")
        print(f"Hotkey: {score_data['hotkey']}")

        print(f"Merkle root: {score_data['merkle_root']}")
        print(f"Actual length: {score_data['actual_len']}")

        print(f"Score data saved to {parent_dir / 'score.json'}")

        return 0
    except Exception as e:
        print(f"Error validating miner: {str(e)}")
        return 1


def validate_all_miners(args):
    """
    Generate merkle trees for all miners in a directory.

    Args:
        args: Command line arguments containing the input_path path
    """
    try:
        # Check if input_path is provided, if not use the default from score_all
        input_path_str = getattr(args, "input_path", None)
        if not input_path_str:
            default_path = "data/input_data.json"
            print(
                f"Warning: --path parameter was omitted, attempting with default path: {default_path}"
            )
            input_path = Path(default_path)
        else:
            input_path = Path(input_path_str)

        if not input_path.exists():
            print(f"Error: Path not found at {input_path}")
            return 1

        print(f"Validating all miners using data from {input_path}")

        # Determine if the input path is a directory or a file
        if input_path.is_dir():
            # If it's a directory, assume it's the children directory
            children_dir = input_path

            # Score all children directly from the directory
            scores = {}
            child_dirs = [d for d in children_dir.iterdir() if d.is_dir()]

            if not child_dirs:
                print("No child directories found.")
                return 1

            for child_dir in child_dirs:
                hotkey = child_dir.name
                print(f"\nScoring child: {hotkey}")

                score_data = score_child(str(child_dir))
                if score_data:
                    scores[hotkey] = score_data

            # Save all scores to a summary file
            summary_file = input_path.parent / "scores_summary.json"
            try:
                with open(summary_file, "w") as f:
                    json.dump(scores, f, indent=2)
                print(f"\nAll scores saved to {summary_file}")
            except Exception as e:
                print(f"Error saving scores summary: {e}")
        else:
            # If it's a file, use the existing score_all function
            scores = score_all(str(input_path))

        if not scores:
            print("Error: Failed to validate miners")
            return 1

        print(f"Successfully validated {len(scores)} miners")
        print(f"Scores saved to {input_path.parent / 'scores_summary.json'}")

        # Print summary
        print("\nValidation Summary:")
        for hotkey, score_data in scores.items():
            print(f"Hotkey: {hotkey[:8]}... - Signals: {score_data['actual_len']}")

        return 0
    except Exception as e:
        print(f"Error validating all miners: {str(e)}")
        return 1


def analyse_data(args):
    """
    Analyze input data and split it into separate files for each hotkey.

    Args:
        args: Command line arguments containing the path to the input JSON file
    """
    try:
        # Check if input_file is provided, if not use the default from split_input_json
        input_file_str = getattr(args, "input_file", None)
        if not input_file_str:
            default_input = "../data/input_data.json"
            print(
                f"Warning: --path parameter was omitted, attempting with default path: {default_input}"
            )
            input_file = Path(default_input)
        else:
            input_file = Path(input_file_str)

        if not input_file.exists():
            print(f"Error: Input file not found at {input_file}")
            return 1

        print(f"Analyzing data from {input_file}...")

        # Call the split_input_json function from analyze_data module
        output_dir_str = getattr(args, "output_dir", None)
        if not output_dir_str:
            default_output = "../data/children"
            print(
                f"Note: --output parameter was omitted, using default output directory: {default_output}"
            )
            output_dir = default_output
        else:
            output_dir = output_dir_str

        count = split_input_json(str(input_file), output_dir)

        if count == 0:
            print("No data was processed. Check the input file format.")
            return 1

        print(f"Successfully analyzed data and split it into {count} files.")
        return 0
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        return 1


def save_tree(args):
    """
    Save a merkle tree from a tree.json file or a hotkey directory to a specified output path.

    Args:
        args: Command line arguments containing the path to the tree.json file or hotkey directory
              and the output path
    """
    try:
        tree_file, _ = _handle_tree_file_path(getattr(args, "path", None))
        if not tree_file:
            return 1

        # Load the tree data
        try:
            with open(tree_file, "r") as f:
                tree_data = json.load(f)
        except Exception as e:
            print(f"Error loading tree data: {e}")
            return 1

        # Check if output_path is provided
        output_path_str = getattr(args, "output_path", None)
        if not output_path_str:
            print(
                "Warning: --output parameter was omitted, please provide an output path."
            )
            return 1

        # Save the tree data to the specified location
        output_path = Path(output_path_str)

        # If output_path is a directory, append tree.json to it
        if output_path.is_dir():
            output_file = output_path / "tree.json"
        else:
            # Otherwise use the provided path directly
            output_file = output_path

        try:
            # Create directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(tree_data, f, indent=2)
            print(f"Tree data saved to {output_file}")
        except Exception as e:
            print(f"Error saving tree data: {e}")
            return 1

        return 0
    except Exception as e:
        print(f"Error saving tree: {str(e)}")
        return 1


def print_header():
    """
    Prints the ASCII art header for the CLI.
    """
    # Check if the terminal supports colors
    import os
    import platform

    # Default to colored output
    use_colors = True

    # Check if NO_COLOR environment variable is set (standard way to disable color)
    if os.environ.get("NO_COLOR") is not None:
        use_colors = False
    # Check if we're running on Windows without proper ANSI support
    elif platform.system() == "Windows" and not os.environ.get("ANSICON"):
        try:
            import colorama

            colorama.init()
        except ImportError:
            use_colors = False

    try:
        from ._version import __version__

        VERSION = __version__
    except ImportError:
        VERSION = "1.0.0"

    # ANSI color codes
    if use_colors:
        BLUE = "\033[34m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        CYAN = "\033[36m"
        RESET = "\033[0m"
    else:
        BLUE = GREEN = YELLOW = CYAN = RESET = ""

    header = f"""
    {CYAN}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}
    {CYAN}║{RESET}                                                                                {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}██████╗ ██████╗  ██████╗  ██████╗ ███████╗{RESET}                                   {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}██╔══██╗██╔══██╗██╔═══██╗██╔═══██╗██╔════╝{RESET}                                   {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}██████╔╝██████╔╝██║   ██║██║   ██║█████╗{RESET}                                     {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}██╔═══╝ ██╔══██╗██║   ██║██║   ██║██╔══╝{RESET}                                     {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}██║     ██║  ██║╚██████╔╝╚██████╔╝██║{RESET}                                        {CYAN}║{RESET}
    {CYAN}║{RESET}   {BLUE}╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝{RESET}                                        {CYAN}║{RESET}
    {CYAN}║{RESET}                                                                                {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW} ██████╗  ███████╗{RESET}                                                           {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW}██╔═══██╗╗██╔════╝{RESET}                                                           {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW}██║   ██║║█████╗{RESET}                                                             {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW}██║   ██║║██╔══╝{RESET}                                                             {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW}╚██████╔╝╝██║{RESET}                                                                {CYAN}║{RESET}
    {CYAN}║{RESET}   {YELLOW} ╚═════╝ ╚═╝{RESET}                                                                 {CYAN}║{RESET}
    {CYAN}║{RESET}                                                                                {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ ██╗     ██╗ ██████╗{RESET}       {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗{RESET}      {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}██████╔╝██║   ██║██████╔╝   ██║   █████╗  ██║   ██║██║     ██║██║   ██║{RESET}      {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝  ██║   ██║██║     ██║██║   ██║{RESET}      {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}██║     ╚██████╔╝██║  ██║   ██║   ██║     ╚██████╔╝███████╗██║╚██████╔╝{RESET}      {CYAN}║{RESET}
    {CYAN}║{RESET}   {GREEN}╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝{RESET}       {CYAN}║{RESET}
    {CYAN}║{RESET}                                                                                {CYAN}║{RESET}
    {CYAN}║{RESET}                          {BLUE}ZK Proof Generation Tool{RESET}                              {CYAN}║{RESET}
    {CYAN}║{RESET}                                 {YELLOW}v{VERSION}{RESET}                                         {CYAN}║{RESET}
    {CYAN}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(header)


def check_dependencies():
    """
    Check if required dependencies (bb, nargo) are available.
    If not, install them automatically.
    """
    import shutil
    import os

    # Skip in CI environments
    if os.environ.get("CI") or os.environ.get("POP_SKIP_INSTALL"):
        return

    missing_deps = []

    # Check for bb (Barretenberg)
    if not shutil.which("bb"):
        missing_deps.append("bb")

    # Check for nargo (Noir)
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
            print("You may need to install them manually:")
            if "bb" in missing_deps:
                print(
                    "  - Barretenberg: curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/refs/heads/master/barretenberg/bbup/install | bash && bbup"
                )
            if "nargo" in missing_deps:
                print(
                    "  - Noir: curl -L https://raw.githubusercontent.com/noir-lang/noirup/main/install | bash && noirup"
                )


def main():
    """
    Main entry point for the CLI.
    """
    try:
        # Check and install dependencies if needed
        check_dependencies()

        # Print the header
        print_header()

        parser = argparse.ArgumentParser(
            prog="pop",
            description="Proof of Portfolio CLI",
            epilog="For more information, visit https://github.com/inference-labs-inc/proof-of-portfolio",
        )

        try:
            from ._version import __version__

            version = __version__
        except ImportError:
            version = "1.0.0"

        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {version}"
        )

        subparsers = parser.add_subparsers(
            title="commands", dest="command", help="Command to execute"
        )

        # Generate tree command
        generate_parser = subparsers.add_parser(
            "generate-tree",
            help="Generate a merkle tree for a miner using their data.json file",
            description="Generate a merkle tree, scores, and print the tree for a miner using their data.json file",
        )
        generate_parser.add_argument(
            "--path", dest="data_file", help="Path to the data.json file"
        )
        generate_parser.add_argument(
            "--hotkey",
            help="Miner's hotkey (if not provided, will try to extract from parent directory name)",
        )
        generate_parser.add_argument(
            "--output",
            dest="output_path",
            help="Path where the tree.json file will be saved (if not provided, saves to the same directory as the data.json file)",
        )
        generate_parser.set_defaults(func=generate_tree)

        # Validate command
        validate_parser = subparsers.add_parser(
            "validate",
            help="Generate a merkle tree for a miner as a validator",
            description="Generate a merkle tree for a miner as a validator and score their data",
        )
        validate_parser.add_argument(
            "--path", dest="data_file", help="Path to the miner's data.json file"
        )
        validate_parser.set_defaults(func=validate_miner)

        # Validate-all command
        validate_all_parser = subparsers.add_parser(
            "validate-all",
            help="Generate merkle trees for all miners in a directory",
            description="Process input JSON file or directory containing miner data, and generate a Merkle tree for each miner",
        )
        validate_all_parser.add_argument(
            "--path",
            dest="input_path",
            help="Path to the input JSON file or directory containing miners' data (default: data/input_data.json)",
        )
        validate_all_parser.set_defaults(func=validate_all_miners)

        # Save-tree command
        save_tree_parser = subparsers.add_parser(
            "save-tree",
            help="Save a merkle tree from a tree.json file or a hotkey directory to a specified output path",
            description="Load a merkle tree and save it to a specified location",
        )
        save_tree_parser.add_argument(
            "--path",
            dest="path",
            help="Path to the tree.json file or the directory containing the tree.json file",
        )
        save_tree_parser.add_argument(
            "--output",
            dest="output_path",
            help="Path where the tree.json file will be saved",
        )
        save_tree_parser.set_defaults(func=save_tree)

        # Analyse-data command
        analyse_data_parser = subparsers.add_parser(
            "analyse-data",
            help="Analyze input data and split it into separate files for each hotkey",
            description="Process input JSON file and split it into subdirectories for each hotkey",
        )
        analyse_data_parser.add_argument(
            "--path",
            dest="input_file",
            help="Path to the input JSON file (default: ../data/input_data.json)",
        )
        analyse_data_parser.add_argument(
            "--output",
            dest="output_dir",
            help="Directory where the split files will be saved (default: ../data/children)",
        )
        analyse_data_parser.set_defaults(func=analyse_data)

        # Generate-test-data command (top-level)
        generate_test_data_parser = subparsers.add_parser(
            "generate-test-data", help="Generate a randomized validator checkpoint file"
        )
        generate_test_data_parser.add_argument(
            "--num-miners", type=int, default=10, help="Number of miners to generate."
        )
        generate_test_data_parser.add_argument(
            "--num-cps", type=int, default=200, help="Number of checkpoints per miner."
        )
        generate_test_data_parser.add_argument(
            "--num-positions",
            type=int,
            default=10,
            help="Number of positions per miner.",
        )
        generate_test_data_parser.add_argument(
            "--num-orders", type=int, default=5, help="Number of orders per position."
        )
        generate_test_data_parser.add_argument(
            "--output-file", type=str, help="Path to save the generated file."
        )
        generate_test_data_parser.set_defaults(func=generate_input_data.main)

        # Demo command
        demo_parser = subparsers.add_parser(
            "demo",
            help="Run demo scripts",
            description="Run various demo scripts to test circuit implementations",
        )
        demo_subparsers = demo_parser.add_subparsers(
            title="demos", dest="demo_command", help="Demo to execute"
        )

        # Log-returns demo
        log_returns_parser = demo_subparsers.add_parser(
            "log-returns", help="Run the log-returns demo"
        )
        log_returns_parser.add_argument(
            "--miner-id", type=str, help="Specific miner ID to test"
        )
        log_returns_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        log_returns_parser.add_argument(
            "--max-checkpoints",
            type=int,
            default=200,
            help="Maximum checkpoints to test per miner",
        )
        log_returns_parser.set_defaults(func=demo_log_returns.main)

        # All demos
        all_parser = demo_subparsers.add_parser(
            "all", help="Run all demos sequentially"
        )
        all_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        all_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        all_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        all_parser.set_defaults(func=demo_all.main)

        # Sharpe demo
        sharpe_parser = demo_subparsers.add_parser("sharpe", help="Run the sharpe demo")
        sharpe_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        sharpe_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        sharpe_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        sharpe_parser.set_defaults(func=demo_sharpe.main)

        # Omega demo
        omega_parser = demo_subparsers.add_parser("omega", help="Run the omega demo")
        omega_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        omega_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        omega_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        omega_parser.set_defaults(func=demo_omega.main)

        # Sortino demo
        sortino_parser = demo_subparsers.add_parser(
            "sortino", help="Run the sortino demo"
        )
        sortino_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        sortino_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        sortino_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        sortino_parser.set_defaults(func=demo_sortino.main)

        # Calmar demo
        calmar_parser = demo_subparsers.add_parser("calmar", help="Run the calmar demo")
        calmar_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        calmar_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        calmar_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        calmar_parser.set_defaults(func=demo_calmar.main)

        # T-stat demo
        tstat_parser = demo_subparsers.add_parser(
            "tstat", help="Run the t-statistic demo"
        )
        tstat_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        tstat_parser.add_argument(
            "--bypass-confidence",
            action="store_true",
            help="Whether to bypass confidence check",
        )
        tstat_parser.add_argument(
            "--weighting", action="store_true", help="Whether to use weighted average"
        )
        tstat_parser.set_defaults(func=demo_tstat.main)

        # Drawdown demo
        drawdown_parser = demo_subparsers.add_parser(
            "drawdown", help="Run the drawdown demo"
        )
        drawdown_parser.add_argument(
            "--batch-tests",
            type=int,
            default=10,
            help="Number of miners to test in batch mode",
        )
        drawdown_parser.set_defaults(func=demo_drawdown.main)

        # Main end-to-end demo
        main_demo_parser = demo_subparsers.add_parser(
            "main", help="Run the comprehensive end-to-end demo with proof generation"
        )
        main_demo_parser.add_argument(
            "--hotkey", type=str, help="Specific miner ID to test"
        )
        main_demo_parser.set_defaults(func=demo_main.main)

        # Parse arguments
        args = parser.parse_args()

        # If no command is provided, show help
        if not args.command:
            parser.print_help()
            return 0

        # Execute the appropriate function
        return args.func(args)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
