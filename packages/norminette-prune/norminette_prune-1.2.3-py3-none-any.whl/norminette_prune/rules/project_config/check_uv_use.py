from pathlib import Path


def check_uv_use(errors, current_dir=None):
    """
    Id: 09
    Description : Verify if UV is used in the project by checking for 'uv.lock' in the current directory or subdirectories.

    Tags:
        - configuration

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """
    current_dir = current_dir or Path.cwd()
    uv_lock_file = list(current_dir.rglob("uv.lock"))

    if not uv_lock_file:
        errors.append(
            "UV n'est pas utilise pour ce projet, nous vous recommandons fortement de l'utiliser."
        )

    return errors
