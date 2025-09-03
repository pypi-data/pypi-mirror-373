import re
from pathlib import Path


def check_basemodel_in_payloads(app, errors):
    """
    Id: 20
    Description: Checks if BaseModel (Pydantic) classes are defined in a file named 'payloads.py'.

    Tags:
    - python_files
    - files_content

    Args:
        app (str or Path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)

    for file_path in app_path.rglob("*.py"):
        if file_path.name == "payloads.py":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        basemodel_pattern = r"class\s+\w+\s*\(\s*.*?BaseModel\b.*?\s*\)"

        if re.search(basemodel_pattern, content):
            rel_path = (
                file_path.relative_to(app_path.parent)
                if app_path.parent in file_path.parents
                else file_path
            )
            errors.append(
                f"\n🚨 Pydantic BaseModel au mauvais endroit 🚨\n"
                f"Le fichier {rel_path} contient des classes qui héritent de BaseModel, "
                f"mais ces classes devraient être définies dans un fichier 'payloads.py'.\n"
            )
