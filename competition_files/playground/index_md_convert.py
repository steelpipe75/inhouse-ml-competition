# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "markdown>=3.10.1",
# ]
# ///

import sys
import markdown
import os

md = markdown.Markdown()

if len(sys.argv) != 3:
    print("Usage: python index_md_convert.py <input_markdown_file> <output_html_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(input_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Get GitHub repository information from environment variables
    repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
    repo_name = os.getenv("GITHUB_REPOSITORY_NAME")

    if repo_owner and repo_name:
        colab_base_url = "https://colab.research.google.com/github/"
        colab_path = "competition_files/playground/Colab/sample.ipynb"
        dynamic_colab_link = f"{colab_base_url}{repo_owner}/{repo_name}/blob/main/{colab_path}"
        markdown_content = markdown_content.replace("COLAB_LINK_PLACEHOLDER", dynamic_colab_link)
    else:
        print("Warning: GITHUB_REPOSITORY_OWNER or GITHUB_REPOSITORY_NAME not found in environment variables. Colab link might be incorrect.", file=sys.stderr)


    html_content = md.convert(markdown_content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully converted '{input_file}' to '{output_file}'")
except FileNotFoundError:
    print(f"Error: File not found. Please check the input file path: '{input_file}'")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)