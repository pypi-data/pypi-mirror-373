from pathlib import Path


def check_gitignore_content(errors, current_dir=None):
    """
    Id: 14
    Description: Verify if ".env", ".venv", "__pycache__/", "node_modules/" and "static_root" are in `.gitignore` file

    Tags:
        - configuration

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """
    current_dir = current_dir or Path.cwd()

    gitignore_path = current_dir / ".gitignore"

    if not gitignore_path.exists():
        errors.append(
            "Vous n'avez pas de fichier '.gitignore', il est important d'en avoir un pour un projet sur un repository git."
        )
        return errors

    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = set(line.strip() for line in f.readlines())

    required_entries = [".env", ".venv", "__pycache__/", "node_modules/", "static_root"]
    missing_entries = [
        entrie
        for entrie in required_entries
        if not any(line.startswith(entrie) for line in content)
    ]

    if missing_entries:
        errors.append(
            f"Le fichier .gitignore ne contient pas ces entrées à masquer : {', '.join(missing_entries)}."
        )

    return errors
