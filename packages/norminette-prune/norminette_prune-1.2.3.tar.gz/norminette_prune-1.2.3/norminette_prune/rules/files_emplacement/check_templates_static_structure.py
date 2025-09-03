from pathlib import Path


def check_templates_static_structure(app, errors):
    """
    Id: 03
    Description : Verify that the `static/` and `templates/` folders contain only one subfolder named after the app.

    Tags:
    - architecture

    Args:
        app (str or path): The name or path of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)
    app = app_path.name
    directories = ["templates", "static"]

    for dir_name in directories:
        dir_path = app_path / dir_name
        if not dir_path.exists():
            continue

        list_dir = [item.name for item in dir_path.iterdir()]
        if not list_dir:
            continue

        if len(list_dir) > 1:
            extra_contents = [item for item in list_dir if item != app]
            errors.append(
                f"\n🚨 Structure incorrecte dans `{dir_name}` 🚨\n"
                f"Le dossier `{dir_name}` ne doit contenir que `{app}`, mais d'autres éléments sont présents :\n\n"
                + "\n".join(f"📌 `{item}`" for item in extra_contents)
                + "\n"
            )
        if app not in list_dir:
            errors.append(
                f"\n🚨 Problème dans `{dir_name}` 🚨\n"
                f"Le dossier `{dir_name}` doit contenir un seul sous-dossier nommé `{app}`, mais il est absent.\n"
            )
