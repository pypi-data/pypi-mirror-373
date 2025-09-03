from pathlib import Path


def check_pages_folder_structure(app, errors):
    """
    Id: 02
    Description: Verify if `page.html` files are inside the 'pages/' folder and ensure files in 'pages/'
    are named 'page' (except in 'components', 'sections', and 'layouts' folders).

    Tags:
        - web_files
        - architecture

    Args:
        app (str or path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)
    app = app_path.name
    misplaced_pages = [
        path for path in app_path.rglob("page.html") if "pages" not in path.parts
    ]
    if misplaced_pages:
        errors.append(
            "\n🚨 Fichiers 'page.html' mal placés 🚨\n"
            "Le fichier 'page.html' doit être dans le dossier '/pages'.\n"
            "Les fichiers suivants ne respectent pas cette règle :\n\n"
            + "\n".join(f"📌 '{file}'" for file in misplaced_pages)
            + "\n"
        )
    templates_dir = app_path / "templates" / app / "pages"
    if templates_dir.exists():
        wrong_files = []
        wrong_files = [
            file
            for file in templates_dir.rglob("*.html")
            if not file.name.startswith("page.")
            and not any(
                part in {"layout", "sections", "components"} for part in file.parts
            )
        ]
        if wrong_files:
            errors.append(
                "\n🚨 Fichiers incorrects dans '/pages' 🚨\n"
                "Tous les fichiers dans '/pages' doivent commencer par 'page.', excepté ceux dans des dossiers '/components', '/sections' ou '/layout'\n"
                "Les fichiers suivants ne respectent pas cette convention :\n\n"
                + "\n".join(f"📌 '{file}'" for file in wrong_files)
                + "\n"
            )
