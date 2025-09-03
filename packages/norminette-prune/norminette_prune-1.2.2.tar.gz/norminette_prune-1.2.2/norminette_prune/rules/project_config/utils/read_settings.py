from pathlib import Path


def read_settings(errors, current_dir=None):
    """
    Description : Reads the content of the `settings.py` file.

    Args:
        errors (list): A list to store error messages if the file is not found.
        current_dir (Path, optional): Directory to search for settings.py. Defaults to current working directory.
    """
    current_dir = current_dir or Path.cwd()

    settings_file = list(current_dir.rglob("settings.py"))

    if not settings_file:
        errors.append(
            "Vous n'avez pas de fichier 'settings.py', il est important d'en avoir un pour un projet Django."
        )
        return errors

    with open(settings_file[0], "r", encoding="utf-8") as f:
        return f.read()
