
import shutil
import sys

def main(directory_path):
    try:
        # Use shutil.rmtree to remove the directory and its contents
        shutil.rmtree(directory_path)
        print(f"Successfully removed everything from {directory_path}")
    except Exception as e:
        print(f"Error while removing contents: {e}")

if __name__ == "__main__":
    file_path = sys.argv[1]
    main(file_path)

