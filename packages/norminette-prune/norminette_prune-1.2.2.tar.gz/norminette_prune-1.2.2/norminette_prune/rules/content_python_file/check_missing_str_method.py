from pathlib import Path


def check_missing_str_method(app, errors):
    """
    Id: 18
    Description : Checks if '__str__' method is present on `models.py`.

    Tags:
    - python_files
    - files_content

    Args:
    app (str or Path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)
    model_file = app_path / "models.py"

    if not model_file.exists():
        return

    with open(model_file, "r", encoding="utf-8") as f:
        content = f.read()
        if not content:
            return
        if "__str__" not in content:
            errors.append(
                "\n🚨 Méthode __str__ manquante 🚨\n"
                "Le fichier 'models.py' ne possèdent pas de méthode '__str__'."
            )
