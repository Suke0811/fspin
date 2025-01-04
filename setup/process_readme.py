import re
import sys
import os
import sys
sys.path.append(".")
from setup import package_info as info
from setuptools_scm import get_version

def generate_readme():
    # Paths relative to the script's directory
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, "readme.template.md")
    output_path = os.path.join(script_dir, "../readme.md")

    # Load the template file
    with open(template_path, 'r') as template_file:
        readme_content = template_file.read()

    # Retrieve the GitHub username dynamically from the environment
    username = os.getenv('GITHUB_REPOSITORY', 'unknown/unknown').split('/')[0]
    repo_name = os.getenv('GITHUB_REPOSITORY', 'unknown/unknown').split('/')[1]

    try:
        package_version =  get_version(root=os.path.dirname(os.path.abspath(__file__)), fallback_version="0.0.0")
    except Exception as e:
        print(f"Error retrieving package version: {e}", file=sys.stderr)
        package_version = "0.0.0"

    placeholders = {
        '<PACKAGE_NAME>': info.PACKAGE_NAME,
        '<PACKAGE_DESCRIPTION>': info.PACKAGE_DESCRIPTION,
        '<USERNAME>': username,
        '<REPOSITORY_NAME>': repo_name,
        '<PACKAGE_VERSION>': package_version,
    }

    # Replace placeholders
    for placeholder, value in placeholders.items():
        readme_content = re.sub(re.escape(placeholder), value, readme_content)

    # Write the processed README
    with open(output_path, 'w') as readme_file:
        readme_file.write(readme_content)

if __name__ == "__main__":
    generate_readme()
