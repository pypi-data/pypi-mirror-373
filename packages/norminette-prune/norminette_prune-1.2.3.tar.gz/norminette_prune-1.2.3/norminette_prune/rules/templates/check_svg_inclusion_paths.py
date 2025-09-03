import re
from pathlib import Path


def check_svg_inclusion_paths(app, errors):
    """
    Id: 07
    Description: Ensure that SVG includes use absolute paths.

    Tags:
    - web_files
    - files_content

    Args:
        app (Path or str): Le chemin vers l'application Django.
        errors (list): A list to store error messages if the structure is incorrect.
    """
    svg_pattern = re.compile(r"\{\% include [\"'](\./|\.\./).*?/svg/.*?\.html[\"']")
    svg_incorrects = []
    for file_path in Path(app).rglob("*.html"):
        with file_path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if svg_pattern.search(line):
                    svg_incorrects.append(f"{file_path}:{i}: {line.strip()}")

    if svg_incorrects:
        errors.append(
            "\n🚨 Problèmes d'inclusion des fichiers SVG 🚨\n"
            "Les fichiers SVG doivent être inclus avec un chemin absolu, pas relatif ('../' ou './').\n"
            "Les inclusions incorrectes sont détectées dans les fichiers suivants :\n\n"
            + "\n".join([f"- {line}" for line in svg_incorrects])
        )
