import sys
import subprocess
from rich import print
import os
from pathlib import Path
from spml2.utils_init import create_example_files
import warnings

warnings.filterwarnings("ignore")


def create_from_template(module_: str = "models_user", current_folder: str = "."):
    import spml2

    package_dir = Path(spml2.__file__).parent
    templates_dir = package_dir / "templates"
    file_path = Path(current_folder) / f"{module_}.py"
    if not file_path.exists():
        with (
            open(templates_dir / f"{module_}.py", "r") as src,
            open(file_path, "w") as dst,
        ):
            dst.write(src.read())
        return True
    return False


def create_from_content(
    module_: str = "models_user", content: str = "", current_folder: str = "."
):

    file_path = Path(current_folder) / f"{module_}.py"
    if not file_path.exists():
        with open(file_path, "w") as dst:
            dst.write(content)
        return True
    return False


def init_user_files(current_folder: str = "."):
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
        if create_from_content(module_, content, current_folder):
            created.append(module_)
    if created:
        for file in created:
            print(f"Created: {file}")
    else:
        print("[+] Initial files already exist.")


def init_user_filesOld(current_folder: str = "."):

    create_example_files()
    created = [
        module_
        for module_ in ["models_user", "options_user", "spml2_main"]
        if create_from_template(module_, current_folder)
    ]
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
    if len(sys.argv) < 2:
        print("Usage: spml2 web or spml2 init")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    create_example_files()

    if cmd == "web":
        init_user_files()
        web_path = get_package_file_path("web.py")
        args = sys.argv[2:]
        subprocess.run(["streamlit", "run", web_path, *args])
        sys.exit(0)
    if cmd == "init":
        init_user_files()
        sys.exit(0)


if __name__ == "__main__":
    console_main()
