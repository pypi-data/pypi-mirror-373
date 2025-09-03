import json
import os
import subprocess
import toml
import re
from . import requires_dependencies


class Miner:
    def __init__(self, ss58_address, name):
        self.name = name
        self.ss58_address = ss58_address
        current_dir = os.path.dirname(os.path.abspath(__file__))

        package_tree_dir = os.path.join(current_dir, "tree_generator")
        dev_tree_dir = os.path.abspath(
            os.path.join(current_dir, "..", "tree_generator")
        )

        if os.path.exists(package_tree_dir):
            self.TREE_GEN_DIR = package_tree_dir
        elif os.path.exists(dev_tree_dir):
            self.TREE_GEN_DIR = dev_tree_dir
        else:
            raise FileNotFoundError(
                f"tree_generator directory not found. Tried: {package_tree_dir}, {dev_tree_dir}"
            )

        self.TREE_GEN_PROVER_TOML = os.path.join(self.TREE_GEN_DIR, "Prover.toml")
        self.MAX_SIGNALS = 256

    def prepare_signals_from_data(self, data_json_path):
        """
        Reads the data.json file for a hotkey, extracts all their orders,
        and transforms them into a list of TradingSignal dicts for the circuits.

        Args:
            data_json_path (str): Path to the data.json file

        Returns:
            tuple: (padded_signals, actual_len)
        """
        print(f"Preparing signals from {data_json_path}...")
        try:
            with open(data_json_path, "r") as f:
                positions = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Data file not found at {data_json_path}")
            return None, 0
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode JSON from {data_json_path}")
            return None, 0

        if not positions:
            print(f"Warning: No positions found in {data_json_path}")
            return [], 0

        orders = []

        if isinstance(positions, dict):

            if "positions" in positions:
                position_list = positions["positions"]
            else:
                print(f"Warning: Unexpected data structure for {data_json_path}")
                return [], 0
        else:
            position_list = positions

        orders = []
        for position in position_list:
            orders.extend(position.get("orders", []))

        orders.sort(key=lambda o: o["processed_ms"])

        signals = []

        for i in range(0, len(orders), 2):
            if (i + 1) >= len(orders) or len(signals) >= self.MAX_SIGNALS:
                break

            open_order = orders[i]
            close_order = orders[i + 1]

            # Map string order types to numeric codes for the circuit
            # Use unsigned values: LONG -> 1, SHORT -> 2, FLAT -> 0
            order_type_map = {"SHORT": 2, "LONG": 1, "FLAT": 0}
            order_type_code = order_type_map.get(open_order["order_type"], 0)

            # Convert UUIDs to single Field (as per main circuit)
            open_uuid_hex = open_order["order_uuid"].replace("-", "")
            close_uuid_hex = close_order["order_uuid"].replace("-", "")
            # Create open signal using main circuit structure
            signals.append(
                {
                    "trade_pair": "0",  # Use 0 for now, could map trade pairs later
                    "order_type": str(order_type_code),
                    "leverage": str(int(abs(open_order["leverage"]) * 100)),
                    "price": str(int(open_order["price"] * 100)),
                    "processed_ms": str(open_order["processed_ms"]),
                    "order_uuid": f"0x{open_uuid_hex}",
                    "bid": str(int(open_order.get("bid", 0) * 100)),
                    "ask": str(int(open_order.get("ask", 0) * 100)),
                }
            )

            # Create close signal using main circuit structure
            signals.append(
                {
                    "trade_pair": "0",  # Use 0 for now, could map trade pairs later
                    "order_type": "0",  # Close orders are FLAT = 0
                    "leverage": str(
                        int(abs(open_order["leverage"]) * 100)
                    ),  # Same leverage as open
                    "price": str(int(close_order["price"] * 100)),
                    "processed_ms": str(close_order["processed_ms"]),
                    "order_uuid": f"0x{close_uuid_hex}",
                    "bid": str(int(close_order.get("bid", 0) * 100)),
                    "ask": str(int(close_order.get("ask", 0) * 100)),
                }
            )

        actual_len = len(signals)
        if actual_len == 0:
            print(f"Warning: No valid order pairs found in {data_json_path}")
            return [], 0

        # Pad signals if we have fewer than MAX_SIGNALS using main circuit structure
        padded_signals = signals + [
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
        ] * (self.MAX_SIGNALS - actual_len)

        print(f"Successfully prepared {actual_len} signals.")
        return padded_signals, actual_len

    def run_merkle_generator(self, signals, actual_len):
        """
        Runs the merkle_generator circuit and parses the witness file to get the output.

        Args:
            signals (list): List of trading signals
            actual_len (int): Actual number of signals

        Returns:
            tuple: (merkle_root, path_elements, path_indices) or None if failed
        """
        print("Running Merkle Generator circuit...")

        merkle_input = {"signals": signals, "actual_len": actual_len}

        witness_name = "merkle_witness"
        witness_path = os.path.join(self.TREE_GEN_DIR, "target", f"{witness_name}.gz")

        with open(self.TREE_GEN_PROVER_TOML, "w") as f:
            toml.dump(merkle_input, f)

        # Find nargo executable
        nargo_cmd = "nargo"
        # Common locations for nargo
        nargo_paths = [
            os.path.expanduser("~/.nargo/bin/nargo"),
            os.path.expanduser("~/.noir/bin/nargo"),
            os.path.expanduser("~/.cargo/bin/nargo"),
            os.path.expanduser("~/.noirup/bin/nargo"),
        ]

        # Check if nargo exists in common locations
        for path in nargo_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                nargo_cmd = path
                print(f"Found nargo at: {nargo_cmd}")
                break

        print("Executing nargo... (This might take a moment)")
        result = subprocess.run(
            [nargo_cmd, "execute", witness_name, "--silence-warnings"],
            cwd=self.TREE_GEN_DIR,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("Merkle generator execution failed!")
            print(result.stderr)
            return None

        print(
            f"Merkle generator executed successfully. Witness saved to {witness_path}"
        )

        try:
            output_str = result.stdout

            def parse_array_from_output(array_name, s):
                pattern = re.compile(rf'"{array_name}": Vec\((.*?)\), "', re.DOTALL)
                match = pattern.search(s)
                if not match:
                    raise ValueError(f"Could not find {array_name} in output")

                array_content = match.group(1)

                field_strs = re.findall(r"Field\(([^)]+)\)", array_content)

                PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617
                values = []
                for field_str in field_strs:
                    val = int(field_str)
                    if val < 0:
                        val = PRIME + val  # Convert negative to positive field element
                    values.append(str(val))
                return values

            root_match = re.search(r'"root": Field\(([^)]+)\)', output_str)
            if not root_match:
                raise ValueError("Could not parse Merkle root from output.")

            PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617
            root_val = int(root_match.group(1))
            if root_val < 0:
                root_val = PRIME + root_val
            merkle_root = str(root_val)

            path_elements_flat = parse_array_from_output("path_elements", output_str)
            path_indices_flat = parse_array_from_output("path_indices", output_str)

            merkle_depth = 8

            path_elements = [
                path_elements_flat[i : i + merkle_depth]
                for i in range(0, len(path_elements_flat), merkle_depth)
            ]
            path_indices = [
                path_indices_flat[i : i + merkle_depth]
                for i in range(0, len(path_indices_flat), merkle_depth)
            ]

            print("Successfully parsed Merkle tree data from circuit output.")
            return merkle_root, path_elements, path_indices

        except Exception as e:
            print(f"Failed to parse Merkle generator output: {e}")
            print("Raw output:", result.stdout)
            return None

    @requires_dependencies
    def generate_tree(self, input_json_path: str, output_path: str = None):
        """
        Generates a Merkle tree from a child hotkey data.json file and saves it to the specified path.

        Args:
            input_json_path (str): Path to the child hotkey data.json file
            output_path (str, optional): Path where the tree.json file will be saved.
                                    If not provided, saves to the same directory as the input file.

        Returns:
            dict: Tree data containing merkle_root, path_elements, and path_indices, or None if failed
        """
        # Prepare signals from the data.json file
        signals, actual_len = self.prepare_signals_from_data(input_json_path)
        if not signals or actual_len == 0:
            print("Could not prepare signals. Exiting.")
            return None

        # Run Merkle Generator
        merkle_data = self.run_merkle_generator(signals, actual_len)
        if not merkle_data:
            print("Halting due to error in Merkle generation.")
            return None

        merkle_root, path_elements, path_indices = merkle_data

        # Create tree data dictionary
        tree_data = {
            "merkle_root": merkle_root,
            "path_elements": path_elements,
            "path_indices": path_indices,
            "actual_len": actual_len,
        }

        # Determine where to save the tree data
        if output_path:
            # If output_path is a directory, append tree.json to it
            if os.path.isdir(output_path):
                tree_file = os.path.join(output_path, "tree.json")
            else:
                # Otherwise use the provided path directly
                tree_file = output_path
        else:
            # Default: save to the same directory as the input file
            output_dir = os.path.dirname(input_json_path)
            tree_file = os.path.join(output_dir, "tree.json")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(tree_file)), exist_ok=True)

            with open(tree_file, "w") as f:
                json.dump(tree_data, f, indent=2)
            print(f"Tree data saved to {tree_file}")
        except Exception as e:
            print(f"Error saving tree data: {e}")
            return None

        # Clean up temporary files
        if os.path.exists(self.TREE_GEN_PROVER_TOML):
            os.remove(self.TREE_GEN_PROVER_TOML)

        merkle_witness_path = os.path.join(
            self.TREE_GEN_DIR, "target", "merkle_witness.gz"
        )
        if os.path.exists(merkle_witness_path):
            os.remove(merkle_witness_path)

        return tree_data

    def visualize_tree(self, tree_data):
        """
        Visualizes the merkle tree in a user-friendly format with ASCII art.
        Only shows the first "actual_len" path elements, ignoring filler paths.

        Args:
            tree_data (dict): Tree data containing merkle_root, path_elements, and path_indices

        Returns:
            str: A string representation of the tree with ASCII art
        """
        if not tree_data:
            return "No tree data available."

        # Extract data from tree_data
        merkle_root = tree_data["merkle_root"]
        path_elements = tree_data["path_elements"]
        path_indices = tree_data.get("path_indices", [])
        actual_len = tree_data.get("actual_len", 0)

        # Box width - adjust as needed
        box_width = 70
        content_width = box_width - 2  # Account for borders

        # Helper function to shorten hash strings
        def shorten_hash(hash_str):
            hash_str = str(hash_str)
            if len(hash_str) <= 14:
                return hash_str
            return f"{hash_str[:6]}...{hash_str[-6:]}"

        # Start building the tree visualization
        tree_str = []
        title = f"🌳 Merkle Tree (Signals: {actual_len}) 🌳"
        tree_str.append(title)
        tree_str.append("═" * box_width)

        # Create a shortened version of the merkle root for display
        if isinstance(merkle_root, str):
            merkle_root_str = merkle_root
        else:
            merkle_root_str = str(merkle_root)
        short_root = shorten_hash(merkle_root_str)

        tree_str.append(f"Root: {short_root}")
        tree_str.append("╔" + "═" * (box_width - 2) + "╗")

        # Determine how many paths to show - only show up to actual_len paths
        max_paths_to_show = min(actual_len, len(path_elements))

        # Create a more tree-like visualization
        for i in range(max_paths_to_show):
            # Get the path elements and indices for this path
            elements = path_elements[i]
            indices = path_indices[i] if i < len(path_indices) else []

            # Add path header
            path_header = f"║ Path {i+1}:"
            if i == 0:
                tree_str.append(
                    path_header + " " * (content_width - len(path_header)) + "║"
                )
            else:
                tree_str.append("║" + "─" * (box_width - 2) + "║")
                tree_str.append(
                    path_header + " " * (content_width - len(path_header)) + "║"
                )

            # Display each level of the path with ASCII art
            for level, element in enumerate(elements):
                # Create a shortened version of the element for display
                short_element = shorten_hash(element)

                # Get the direction (left/right) if available
                direction = ""
                if level < len(indices):
                    direction = "→ Right" if indices[level] == "1" else "→ Left"

                # Create tree-like structure with ASCII art
                # Limit the depth of visualization to prevent excessive indentation
                max_visible_depth = 4
                if level == 0:
                    prefix = "║ ├── "
                elif level < max_visible_depth:
                    prefix = "║ │   " * level + "├── "
                else:
                    # For deeper levels, use a more compact representation
                    prefix = (
                        "║ │   " * (max_visible_depth - 1)
                        + "├─"
                        + "─" * (level - max_visible_depth + 1)
                        + " "
                    )

                # Add the line to the tree
                node_info = f"Level {level+1}: {short_element} {direction}"
                line = f"{prefix}{node_info}"

                # Ensure the line fits within the box
                if len(line) > box_width - 1:
                    # Calculate available space for node_info
                    available_space = box_width - 1 - len(prefix) - 3  # -3 for "..."
                    # Truncate node_info to fit
                    truncated_node_info = node_info[:available_space] + "..."
                    line = f"{prefix}{truncated_node_info}"

                # Pad the line to fill the box width
                tree_str.append(line + " " * (box_width - 1 - len(line)) + "║")

        # If there are more paths, indicate that
        if len(path_elements) > max_paths_to_show:
            tree_str.append("║" + "─" * (box_width - 2) + "║")
            more_paths_msg = (
                f"║ ... {len(path_elements) - max_paths_to_show} more paths ..."
            )
            tree_str.append(
                more_paths_msg + " " * (box_width - 1 - len(more_paths_msg)) + "║"
            )

        # Close the box
        tree_str.append("╚" + "═" * (box_width - 2) + "╝")

        return "\n".join(tree_str)

    def __str__(self):
        return self.name
