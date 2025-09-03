from pathlib import Path


def check_pyproject_configuration(errors, current_dir=None):
    """
    Id: 10
    Description: Verify if pyproject.toml exist and contain pydantic, ipython and whitenoise

    Tags:
        - configuration

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """
    current_dir = current_dir or Path.cwd()
    pyproject_file = list(current_dir.rglob("pyproject.toml"))

    if not pyproject_file:
        errors.append(
            "Vous n'avez pas de fichier 'pyproject.toml', il est important d'en avoir un pour configurer le projet"
        )
        return errors

    with open(pyproject_file[0], "r", encoding="utf-8") as f:
        content = f.read()

    required_packages = ["pydantic", "ipython", "whitenoise"]
    missing_packages = [pkg for pkg in required_packages if pkg not in content]

    if missing_packages:
        errors.append(
            f"Le fichier 'pyproject.toml' ne contient pas cette / ces dépendance(s) requises : {', '.join(missing_packages)}."
        )

    return errors
