import sys
import subprocess
from rich import print
import os
from pathlib import Path
from spml2.utils_init import create_example_files
import warnings

warnings.filterwarnings("ignore")


def create_from_content(
    module_: str = "models_user",
    content: str = "",
    current_folder: str = ".",
    force: bool = False,
):

    file_path = Path(current_folder) / f"{module_}.py"
    if not file_path.exists() or force:
        with open(file_path, "w") as dst:
            dst.write(content)
        return True
    return False


def init_user_files(current_folder: str = ".", force: bool = False):
    from .templates_content.models_ import models_content
    from .templates_content.options_ import options_content
    from .templates_content.main_ import main_content

    create_example_files()
    created = []
    for module_, content in [
        ("models_user", models_content),
        ("options_user", options_content),
        ("spml2_main", main_content),
    ]:
        if create_from_content(module_, content, current_folder, force=force):
            created.append(module_)
    if created:
        for file in created:
            print(f"Created: {file}")
    else:
        print("[+] Initial files already exist.")


def get_package_file_path(filename):
    import spml2

    package_dir = os.path.dirname(spml2.__file__)
    return os.path.join(package_dir, filename)


def console_main():
    help_message = """\
SPML2 Command Line Interface

Usage:
  spml2 web         # Launch the web UI
  spml2 init        # Create example user files in the current directory
  spml2 init -f     # Force overwrite example user files even if they exist

Examples:
  spml2 web
  spml2 web --server.port 8502
  spml2 init
  spml2 init -f
"""
    if len(sys.argv) < 2:
        print(help_message)
        sys.exit(1)

    cmd = sys.argv[1].lower()
    create_example_files()
    if cmd in ["help", "--help", "-h"]:

        print(help_message)
        sys.exit(0)

    if cmd == "web":
        init_user_files()
        web_path = get_package_file_path("web.py")
        args = sys.argv[2:]
        subprocess.run(["streamlit", "run", web_path, *args])
        sys.exit(0)
    if cmd == "init":
        force = len(sys.argv) > 2 and sys.argv[2] == "-f"
        init_user_files(force=force)
        sys.exit(0)

    # Unknown command
    print(f"Unknown command: {cmd}\n")
    print(help_message)
    sys.exit(1)


if __name__ == "__main__":
    console_main()
