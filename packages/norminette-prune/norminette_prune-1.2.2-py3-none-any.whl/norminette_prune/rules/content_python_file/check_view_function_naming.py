import re
from pathlib import Path


def check_view_function_naming(app, errors):
    """
    Id: 01
    Description : Verify that the name of rendering functions for views ends with '_view'.

    Tags:
    - python_files
    - files_content

    Args:
        app (str or path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """

    app_path = Path(app)
    view_files = []

    for path in app_path.rglob("*.py"):
        if path.name == "views.py" and path.stem != "utils":
            view_files.append(path)
        elif path.parent.name == "views" and path.name not in {
            "__init__.py",
            "utils.py",
        }:
            view_files.append(path)

    if not view_files:
        return

    erreurs_fonctions = []

    for view_file in view_files:
        with open(view_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fonctions_detectees = []
        fonction_actuelle = None
        ligne_fonction = None

        for i, line in enumerate(lines, start=1):
            match_fonction = re.match(r"^\s*def\s+(\w+)\(", line)
            if match_fonction:
                fonction_actuelle = match_fonction.group(1)
                ligne_fonction = i

            if "render(" in line and fonction_actuelle:
                fonctions_detectees.append(
                    (fonction_actuelle, view_file, ligne_fonction)
                )

        for nom_fonction, fichier, ligne in fonctions_detectees:
            if not nom_fonction.endswith("_view"):
                erreurs_fonctions.append(
                    f"📌 {nom_fonction} → `{fichier}` (ligne {ligne})"
                )

    if erreurs_fonctions:
        errors.append(
            "\n🚨 Problèmes de nommage des fonctions de vue 🚨\n"
            "Les fonctions qui utilisent 'render()' doivent se terminer par '_view'.\n"
            "Voici les fonctions mal nommées :\n\n"
            + "\n".join(erreurs_fonctions)
            + "\n"
        )
