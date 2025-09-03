from pathlib import Path


def check_core_model_exists(errors, base_path=Path(".")):
    """
    Id: 16
    Description: Checks if a core model class exists in `lib/models.py`

    Tags:
    - python_files
    - files_content

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """
    lib_folder = base_path / "lib"

    if not lib_folder.exists():
        errors.append(
            "Le projet doit comporter un dossier `lib/` dans lequel on a au moins un fichier 'models.py' avec le model de base CoreModel."
        )
        return errors
    model_file = lib_folder / "models.py"
    if not model_file.exists():
        errors.append(
            "Le projet doit comporter au moins un fichier 'models.py' avec le model de base CoreModel dans le dossier 'lib/'"
        )
        return errors

    with open(model_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "class CoreModel" not in content:
        errors.append(
            "Le fichier 'lib/models.py' doit contenir une classe 'CoreModel' qui sert de modèle de base avec les champs 'updated_at' et 'created_at'."
        )
        return errors
