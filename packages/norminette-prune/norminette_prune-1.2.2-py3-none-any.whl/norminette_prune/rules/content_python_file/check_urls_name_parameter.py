import re
from pathlib import Path


def check_urls_name_parameter(app, errors):
    """
    Id: 19
    Description: Checks if all URL patterns in urls.py have a 'name' parameter.

    Tags:
    - python_files
    - files_content

    Args:
        app (str or Path): The name or path of the Django app to check.
        errors (list): A list to store error messages.
    """
    app_path = Path(app)
    urls_file = app_path / "urls.py"

    if not urls_file.exists():
        return errors

    with open(urls_file, "r", encoding="utf-8") as f:
        content = f.read()

    path_patterns = re.finditer(
        r"(?:path|re_path)\s*\(\s*['\"]([^'\"]+)['\"](?:\s*,[^)]*)?\)", content
    )

    missing_names = []
    line_number = 1

    for match in path_patterns:
        path_def = match.group(0)
        if "name=" not in path_def:
            line_number = content[: match.start()].count("\n") + 1
            path_str_match = re.search(r'["\']([^"\']*)["\']', path_def)
            path_str = path_str_match.group(1) if path_str_match else "unknown"
            missing_names.append(f"- Ligne {line_number}: {path_str}")

    if missing_names:
        errors.append(
            "\n🚨 Paramètre 'name' manquant dans urls.py 🚨\n"
            + "Chaque chemin d'URL doit avoir un paramètre 'name' pour permettre "
            + "l'utilisation de la fonction reverse() et des liens nommés dans les templates.\n"
            + "Les chemins d'URL suivants dans 'urls.py' n'ont pas de paramètre 'name':\n\n"
            + "\n".join(missing_names)
            + "\n"
        )
