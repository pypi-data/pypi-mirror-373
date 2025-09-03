import re
from pathlib import Path


def check_core_model_usage(app, errors):
    """
    Id: 15
    Description : Checks if a model directly inherits from other than CoreModels.

    Tags:
    - python_files
    - files_content

    Args:
        app (str or path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """

    app_path = Path(app)
    model_file = app_path / "models.py"

    if not model_file.exists():
        return

    with open(model_file, "r", encoding="utf-8") as f:
        content = f.read()

    class_pattern = r"class\s+(\w+)\s*\(([^)]*)\)\s*:"

    class_errors = []

    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)
        inheritance = match.group(2)

        if not re.search(
            r"\b(CoreModel|lib\.models\.CoreModel|DatedModel)\b", inheritance
        ):
            line_num = content[: match.start()].count("\n") + 1
            class_errors.append(f"- Ligne {line_num} : {class_name}")

    if class_errors:
        errors.append(
            "\n🚨 Problème d'héritage de modèle Django 🚨\n"
            "Les classes suivantes héritent directement de 'Model' ou 'models.Model', "
            "alors qu'il est recommandé d'utiliser un modèle de base de 'prune' dans 'prune_lib/commons/models.py' :\n\n"
            + "\n".join(class_errors)
            + "\n"
        )
