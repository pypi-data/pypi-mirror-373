import re
import subprocess
from pathlib import Path


def find_norminette_path():
    try:
        chemin = subprocess.check_output(
            "find . -type d -name 'norminette_prune'", shell=True, text=True
        ).strip()
        return Path(chemin) if chemin else None
    except subprocess.CalledProcessError:
        return None


def extract_docstrings():
    """Extract rules documentation by extracting docstring"""
    norminette_path = find_norminette_path()
    if not norminette_path:
        print("🚨 Impossible de trouver le dossier 'norminette_prune'")
        return []

    directory = norminette_path / "rules"
    pattern = re.compile(
        r'def\s+(\w+)\s*\(.*?\):\s+"""\s+Id\s*:\s*(\d+)\s+Description\s*:\s*(.*?)\s+Tags\s*:\s*(.*?)\s+Args\s*:(.*?)"""',
        re.DOTALL,
    )
    results = []

    try:
        if not directory.exists():
            print(f"🚨 Le répertoire n'existe pas : {directory}")
            return results

        for rules_folder in directory.iterdir():
            if not rules_folder.is_dir():
                continue

            for py_file in rules_folder.rglob("*.py"):
                try:
                    with py_file.open("r", encoding="utf-8") as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for match in matches:
                            function_name, rule_id, description, tags, args = match
                            description = " ".join(description.splitlines()).strip()
                            tags_list = " ".join(
                                [t.strip() for t in tags.split("-") if t.strip()]
                            )

                            results.append(
                                (function_name, rule_id, description, tags_list)
                            )
                except Exception as e:
                    print(f"❌ Erreur lors du traitement du fichier {py_file}: {e}")

    except Exception as e:
        print(f"❌ Erreur lors du scan du répertoire : {e}")

    return results


def get_tags_descriptions():
    return {
        "web_files": "HTML, JS, and CSS files.",
        "python_files": "Python files with `.py` extension.",
        "architecture": "Checks folder and file placement consistency.",
        "format": "Directly modifies file formatting.",
        "files_content": "Inspects file contents.",
        "configuration": "Verify project configuration.",
        "content_settings": "Verify settings.py configuration.",
    }


def get_sorted_rules():
    docstrings = extract_docstrings()
    docstrings.sort(key=lambda x: int(x[1]))
    return docstrings
