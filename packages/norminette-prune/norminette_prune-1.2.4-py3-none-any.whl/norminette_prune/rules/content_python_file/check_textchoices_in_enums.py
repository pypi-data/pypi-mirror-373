import re
from pathlib import Path


def check_textchoices_in_enums(app, errors):
    """
    Id: 17
    Description: Checks if TextChoices classes are defined in a file named 'enums.py'.

    Tags:
    - python_files
    - files_content

    Args:
        app (str or Path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)

    for file_path in app_path.rglob("*.py"):
        if file_path.name == "enums.py":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        textchoices_pattern1 = r"class\s+\w+\s*\(\s*models\.TextChoices\s*\)"
        textchoices_pattern2 = r"class\s+\w+\s*\(\s*TextChoices\s*\)"

        if re.search(textchoices_pattern1, content) or re.search(
            textchoices_pattern2, content
        ):
            rel_path = (
                file_path.relative_to(app_path.parent)
                if app_path.parent in file_path.parents
                else file_path
            )
            errors.append(
                f"\n🚨 TextChoices au mauvais endroit 🚨\n"
                f"Le fichier {rel_path} contient des classes TextChoices, "
                f"mais ces classes devraient être définies dans un fichier 'enums.py'.\n"
            )
