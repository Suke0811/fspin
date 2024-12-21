import re
import os
import package_info as info

def generate_readme():
    # Paths relative to the script's directory
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, "readme.template.md")
    output_path = os.path.join(script_dir, "../../readme.md")

    # Load the template file
    with open(template_path, 'r') as template_file:
        readme_content = template_file.read()

    # Retrieve the GitHub username dynamically from the environment
    github_username = os.getenv('GITHUB_USERNAME', 'unknown-user')

    # Dictionary of placeholders to replace
    placeholders = {
        '<PACKAGE_NAME>': info.PACKAGE_NAME,
        '<PACKAGE_DESCRIPTION>': info.PACKAGE_DESCRIPTION,
        '<USERNAME>': github_username,
        '<REPOSITORY_NAME>': info.REPOSITORY_NAME,
    }

    # Replace placeholders
    for placeholder, value in placeholders.items():
        readme_content = re.sub(re.escape(placeholder), value, readme_content)

    # Write the processed README
    with open(output_path, 'w') as readme_file:
        readme_file.write(readme_content)

if __name__ == "__main__":
    generate_readme()
