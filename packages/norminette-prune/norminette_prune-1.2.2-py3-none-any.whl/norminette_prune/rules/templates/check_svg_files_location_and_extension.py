from itertools import chain
from pathlib import Path


def check_svg_files_location_and_extension(app, errors):
    """
    Id: 08
    Description: Verify that SVG files are inside the `svg/` folder and use the `.html` extension.

    Tags:
    - web_files
    - architecture

    Args:
        app (Path or str): Le chemin vers l'application Django.
        errors (list): Liste des erreurs détectées.
    """
    app_path = Path(app)

    wrong_folder_files = []
    wrong_extension_files = []

    for file_path in chain(app_path.rglob("*.html"), app_path.rglob("*.svg")):
        if any(
            skip in file_path.parts
            for skip in [".venv", "whitenoise-root", "static_assets"]
        ):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            if "</svg>" in content:
                parent_dir = file_path.parent.name
                suffix_file = file_path.suffix

                if parent_dir != "svg":
                    wrong_folder_files.append(file_path)

                if suffix_file == ".svg":
                    wrong_extension_files.append(file_path)
        except Exception:
            continue

    if wrong_folder_files:
        errors.append(
            "\n🚨 Fichiers SVG mal placés 🚨\n"
            "Les fichiers contenant des '<svg>' doivent être dans un dossier 'svg/'.\n"
            "Les fichiers suivants sont mal placés :\n"
            + "\n".join([f"- '{file}'" for file in wrong_folder_files])
        )

    if wrong_extension_files:
        errors.append(
            "\n🚨 Fichiers SVG mal nommés 🚨\n"
            "Les fichiers contenant des balises '<svg>' doivent être en '.html', pas en '.svg'.\n"
            "Les fichiers suivants ont la mauvaise extension :\n"
            + "\n".join([f"- '{file}'" for file in wrong_extension_files])
        )
