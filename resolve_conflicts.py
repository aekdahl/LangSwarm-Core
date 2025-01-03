import re
import sys

def resolve_python_version_conflict(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Extract conflicting lines
    start_index, end_index = None, None
    for i, line in enumerate(lines):
        if "<<<<<<<" in line:
            start_index = i
        elif ">>>>>>>" in line:
            end_index = i

    if start_index is None or end_index is None:
        print("No conflict markers found.")
        return

    # Extract Python versions from both conflicts
    conflict_block = lines[start_index:end_index + 1]
    local_versions = re.findall(r"\d+\.\d+", conflict_block[1])
    incoming_versions = re.findall(r"\d+\.\d+", conflict_block[3])

    # Merge and sort unique versions
    merged_versions = sorted(set(local_versions + incoming_versions))

    # Replace conflict block with resolved versions
    resolved_block = [
        f"# Supported versions of Python: {', '.join(merged_versions)}\n"
    ]
    lines[start_index:end_index + 1] = resolved_block

    with open(file_path, "w") as f:
        f.writelines(lines)

    print(f"Resolved conflict in {file_path}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resolve_conflicts.py <file_path>")
        sys.exit(1)

    resolve_python_version_conflict(sys.argv[1])
