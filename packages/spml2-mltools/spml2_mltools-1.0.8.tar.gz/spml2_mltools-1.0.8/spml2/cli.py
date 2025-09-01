import sys
import subprocess
from rich import print
import os
from pathlib import Path


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


def init_user_files(current_folder: str = "."):
    """Create user-editable template files if they do not exist, using templates from the package."""
    created = []
    from spml2.utils_init import create_example_files

    create_example_files()

    for module_ in ["models_user", "options_user", "spml2_main"]:
        create_from_template(module_, current_folder)

    if created:
        for file in created:
            print(f"Created: {file}")
    else:
        print("models_user.py and options_user.py already exist.")


def get_package_file_path(filename):
    import spml2

    package_dir = os.path.dirname(spml2.__file__)
    return os.path.join(package_dir, filename)


def console_main():
    """
    Launches a Streamlit app for the given file or initializes user files.
    Usage: spml2 <file_name.py> or spml2 init
    """
    if len(sys.argv) < 2:
        print("Usage: spml2 <file_name.py> or spml2 init")
        sys.exit(1)
    if sys.argv[1] == "web":
        init_user_files()
        web_path = get_package_file_path("web.py")
        if sys.argv[2:]:
            subprocess.run(["streamlit", "run", web_path, *sys.argv[2:]])
        else:
            subprocess.run(["streamlit", "run", web_path])
        sys.exit(0)

    if sys.argv[1] == "init":
        init_user_files()
        sys.exit(0)


if __name__ == "__main__":
    console_main()
