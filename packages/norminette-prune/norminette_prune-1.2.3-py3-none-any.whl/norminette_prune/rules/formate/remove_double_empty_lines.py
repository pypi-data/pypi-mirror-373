from pathlib import Path


def remove_double_empty_lines(app):
    """
    Id: 04
    Description: Remove double empty lines in HTML, JS, and CSS files.

    Tags:
    - format
    - files_content
    - web_files

    Args:
        app (str or Path): The name or path of the Django app to check.
    """
    app_path = Path(app)
    app = app_path.name

    templates_dir = app_path / "templates" / app

    if templates_dir.exists():
        for file_path in templates_dir.rglob("*.html"):
            _remove_double_empty_lines(file_path)

        for file_path in templates_dir.rglob("*.js"):
            _remove_double_empty_lines(file_path)

        for file_path in templates_dir.rglob("*.css"):
            _remove_double_empty_lines(file_path)


def _remove_double_empty_lines(file_path):
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        previous_line_empty = False

        for line in lines:
            if line.strip() == "":
                if previous_line_empty:
                    continue
                previous_line_empty = True
            else:
                previous_line_empty = False
            new_lines.append(line)

        if new_lines != lines:
            with file_path.open("w", encoding="utf-8") as f:
                f.writelines(new_lines)

    except Exception as e:
        print(f"❌ Erreur lors du traitement du fichier {file_path}: {e}")
