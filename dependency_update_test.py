def update_requirements_with_python_versions(dependency_versions, supported_python_versions):
    """
    Update the requirements.txt file with the latest compatible versions
    and add a comment at the top indicating supported Python versions.
    """
    with open("requirements.txt", "w") as f:
        # Add the comment about supported Python versions
        f.write(f"# Supported versions of Python: {', '.join(supported_python_versions)}\n")
        f.write("# Automatically updated by dependency_update_test.py\n\n")

        # Write the compatible dependency versions
        for package, compatible_version in dependency_versions.items():
            f.write(f"{package}=={compatible_version}\n")
    print("requirements.txt updated successfully with Python version support comment.")

def main(python_version, supported_python_versions):
    # Read dependencies from requirements.txt
    with open("requirements.txt", "r") as f:
        dependencies = [line.strip().split("==")[0] for line in f if "==" in line]

    latest_versions = {}
    for package in dependencies:
        versions = fetch_versions(package)
        if not versions:
            print(f"Skipping {package} (no versions found).")
            continue

        # Test versions from newest to oldest
        compatible_version = None
        for version in versions:
            if test_dependency(package, version):
                compatible_version = version
                break

        if compatible_version:
            print(f"Compatible version for {package}: {compatible_version}")
            latest_versions[package] = compatible_version
        else:
            print(f"No compatible version found for {package} on Python {python_version}.")
            sys.exit(1)  # Exit if no version works for a dependency

    # Update requirements.txt with compatible versions and supported Python versions
    update_requirements_with_python_versions(latest_versions, supported_python_versions)
