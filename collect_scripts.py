import os

# SET START FOLDER AT THE END OF THE SCRIPT

# Function to write all files into a single output file
def collect_scripts(start_folder="START_FOLDER", output_file="collected_scripts.txt"):
    start_path = os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), start_folder)
    if not os.path.exists(start_path):
        print(f"Error: The folder '{start_folder}' does not exist.")
        return

    with open(output_file, "w", encoding="utf-8") as outfile:
        # Walk through the specified folder and its subfolders
        for root, _, files in os.walk(start_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, start_path)

                try:
                    # Write the relative file name and path as a header
                    outfile.write(f"\n{'-'*80}\n")
                    outfile.write(f"File: {relative_path}\n")
                    outfile.write(f"{'-'*80}\n\n")

                    # Read the file content and write it
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                        outfile.write("\n\n")
                except Exception as e:
                    # Log files that couldn't be read
                    outfile.write(f"[ERROR READING FILE: {relative_path} - {e}]\n\n")

if __name__ == "__main__":
    output_filename = "collected_scripts.txt"
    start_folder = "langswarm"
    print(f"Collecting scripts from '{start_folder}' into {output_filename}...")
    collect_scripts(start_folder=start_folder, output_file=output_filename)
    print(f"All scripts have been collected into {output_filename}.")
