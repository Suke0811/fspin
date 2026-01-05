import os
import sys

try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.7
    import importlib_resources as resources

def main():
    # Use importlib.resources to access the cheatsheet bundled in the package
    try:
        # For modern Python (3.9+)
        if hasattr(resources, 'files'):
            cheatsheet_content = resources.files('fspin').joinpath('fspin_cheatsheet.md').read_text(encoding='utf-8')
        else:
            # Fallback for older importlib.resources (Python 3.7, 3.8)
            with resources.open_text('fspin', 'fspin_cheatsheet.md', encoding='utf-8') as f:
                cheatsheet_content = f.read()
        print(cheatsheet_content)
    except Exception:
        # Fallback to local file path if importlib.resources fails (e.g. during development)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cheatsheet_path = os.path.join(current_dir, "fspin_cheatsheet.md")
        
        if os.path.exists(cheatsheet_path):
            with open(cheatsheet_path, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("fspin Cheatsheet not found.")
            print("Please check the online documentation at https://github.com/Suke0811/fspin")

if __name__ == "__main__":
    main()
