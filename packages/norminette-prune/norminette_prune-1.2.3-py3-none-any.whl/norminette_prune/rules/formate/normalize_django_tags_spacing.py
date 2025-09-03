import re
from pathlib import Path


def normalize_django_tags_spacing(app):
    """
    Id: 05
    Description: Normalize spaces in Django tags (with exactly one space between the tag and its content).

    Tags:
    - format
    - web_files
    - files_content

    Args:
        app (str): The name of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    app_path = Path(app)
    app = app_path.name

    templates_dir = app_path / "templates" / app
    if not templates_dir.exists():
        return

    def normalize_spaces(content):
        def normalize_single_tag(match):
            full_tag = match.group(0)

            if full_tag.startswith("{{"):
                inner_content = full_tag[2:-2].strip()
                formatted_tag = "{{ " + inner_content + " }}"
                return formatted_tag
            elif full_tag.startswith("{%"):
                inner_content = full_tag[2:-2].strip()
                formatted_tag = "{% " + inner_content + " %}"
                return formatted_tag
            else:
                return full_tag

        pattern = r"\{\{[^}]*\}\}|\{%[^%]*%\}"
        return re.sub(pattern, normalize_single_tag, content)

    for template_file in templates_dir.rglob("*.html"):
        if template_file.is_file():
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = normalize_spaces(content)

                if new_content != content:
                    with open(template_file, "w", encoding="utf-8") as f:
                        f.write(new_content)

            except Exception as e:
                print(f"❌ Erreur lors du traitement du fichier {template_file}: {e}")
