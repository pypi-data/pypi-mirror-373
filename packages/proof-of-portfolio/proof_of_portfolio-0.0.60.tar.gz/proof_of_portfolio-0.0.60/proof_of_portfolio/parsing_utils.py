"""
Shared parsing utilities for nargo output across all demos.
"""

import re


def parse_single_field_output(output):
    """
    Parses nargo output that contains a single field value.
    Returns the integer value, or None if no field found.
    """
    if "0x" in output:
        hex_match = output.split("0x")[1].split()[0]
        return int(hex_match, 16)

    if "Field(" in output:
        return int(output.split("Field(")[1].split(")")[0])

    if "Circuit output:" in output:
        output_line = output.split("Circuit output:")[1].strip().split()[0]
        return int(output_line)

    lines = output.strip().split("\n")
    for line in lines:
        line = line.strip()
        if (
            line
            and not any(char.isalpha() for char in line)
            and line.replace("-", "").replace(".", "").isdigit()
        ):
            return int(float(line))

    return None


def field_to_signed_int(field_str):
    """
    Convert a field string to a signed integer, handling two's complement.
    """
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


def parse_demo_output(output, scale=10_000_000, no_confidence_value=-100):
    """
    Standardized parsing for demo output.

    Args:
        output: Raw stdout
        scale: Scale factor used in the circuit (default 10M)
        no_confidence_value: Value indicating no confidence result

    Returns:
        Float value scaled appropriately, or the no_confidence_value as-is
    """
    field_value = parse_single_field_output(output)

    if field_value is None:
        raise ValueError(f"Could not parse field value from nargo output: {output}")

    signed_value = field_to_signed_int(field_value)

    # If it's the no confidence marker, return as-is
    if signed_value == no_confidence_value:
        return float(signed_value)

    # Otherwise scale it back
    return signed_value / scale


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

        if part.startswith("0x") and len(part) > 2:
            try:
                values.append(str(int(part, 16)))
                continue
            except ValueError:
                pass

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
