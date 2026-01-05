import os
import sys

def main():
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the cheatsheet (it should be bundled with the package)
    # We look for it in the package directory or the project root
    cheatsheet_path = os.path.join(current_dir, "fspin_cheatsheet.md")
    
    # Fallback for development environment if not found in package dir
    if not os.path.exists(cheatsheet_path):
        cheatsheet_path = os.path.join(current_dir, "..", "fspin_cheatsheet.md")

    if os.path.exists(cheatsheet_path):
        with open(cheatsheet_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("fspin Cheatsheet not found.")
        print("Please check the online documentation at https://github.com/Suke0811/fspin")

if __name__ == "__main__":
    main()
