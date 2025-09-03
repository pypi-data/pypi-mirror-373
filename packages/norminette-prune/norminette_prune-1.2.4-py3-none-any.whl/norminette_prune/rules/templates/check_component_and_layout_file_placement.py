import os
import re
from pathlib import Path


def check_component_and_layout_file_placement(app, errors):
    """
    Id : 06
    Description : Verify that layout, component, and section files are correctly placed based on their `include` references.

    Tags :
    - web_files
    - architecture

    Args:
        app (str): The name of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
    """

    app_path = Path(app)

    component_layout_dict = {
        "components": {
            "pattern": r"{% include\s+[\'\"]([^\'\"]+components[^\'\"]+\.html)[\'\"]",
            "subfolder": "components",
            "entity_name": "composant",
        },
        "sections": {
            "pattern": r"{% include\s+[\'\"]([^\'\"]+sections[^\'\"]+\.html)[\'\"]",
            "subfolder": "sections",
            "entity_name": "section",
        },
        "layout": {
            "pattern": r"{% extends\s+[\'\"]([^\'\"]+layout[^\'\"]+\.html)[\'\"]",
            "subfolder": "layout",
            "entity_name": "layout",
        },
    }

    for key, value in component_layout_dict.items():
        includes_extends_dict = get_includes_extends_paths(app_path, value["pattern"])

        includes_extends_dict = filter_duplicate_files(
            app_path, includes_extends_dict, errors
        )
        includes_extends_dict = resolve_file_paths(
            app_path, Path(app_path).parent, includes_extends_dict, errors
        )
        for component_layout, file_paths in includes_extends_dict.items():
            file_name = Path(component_layout).name
            expected_path = get_expected_path(file_paths, value["subfolder"], file_name)

            if component_layout != expected_path:
                error_message = (
                    f"\n🚨 Fichier mal placé : '{file_name}' 🚨\n"
                    f"- Actuel : '{component_layout}'\n"
                    f"- Attendu : '{expected_path}'\n"
                )
                if not any(
                    file_name in error and "Mauvais placement" in error
                    for error in errors
                ):
                    errors.append(error_message)


def get_includes_extends_paths(app_path, pattern_str):
    includes_extends_dict = {}
    include_extend_pattern = re.compile(pattern_str)

    for html_file in Path(app_path).rglob("*.html"):
        if "svg" in html_file.parts:
            continue

        with html_file.open(encoding="utf-8") as f:
            for line in f:
                match = include_extend_pattern.search(line)
                if match:
                    include_extend_path = match.group(1)
                    file_name = Path(include_extend_path).name
                    includes_extends_dict.setdefault(file_name, set()).add(
                        str(html_file)
                    )

    return includes_extends_dict


def filter_duplicate_files(app_path, includes_extends_dict, errors):
    file_name_map = {}

    for file_name in includes_extends_dict.keys():
        file_name_map[file_name] = [
            p for p in Path(app_path).rglob(file_name) if "svg" not in p.parts
        ]

    duplicate_files = {f: paths for f, paths in file_name_map.items() if len(paths) > 1}

    if duplicate_files:
        error_message = "\n🚨 Problème de fichiers en double 🚨\n"
        for file_name, paths in duplicate_files.items():
            if any(
                file_name in error and "Problème de fichiers en double" in error
                for error in errors
            ):
                continue

            error_message += (
                f"'{file_name}' trouvé dans :\n"
                + "\n".join(f"  - {p}" for p in paths)
                + "\n"
            )

        errors.append(error_message)

    for file_name, paths in duplicate_files.items():
        for path in paths:
            includes_extends_dict.pop(file_name, None)

    return includes_extends_dict


def resolve_file_paths(app_path, project_root, includes_extends_dict, errors):
    updated_dict = {}
    error_messages = []

    for file_name in includes_extends_dict.keys():
        found_path = next(
            (p for p in Path(app_path).rglob(file_name) if "svg" not in p.parts), None
        )

        if found_path:
            updated_dict[str(found_path)] = includes_extends_dict[file_name]
        else:
            found_path = next(
                (
                    p
                    for p in Path(project_root).rglob(file_name)
                    if "svg" not in p.parts
                ),
                None,
            )
            if found_path:
                error_message = (
                    f"\n🚨 Fichier mal placé 🚨\n"
                    f"Le fichier '{file_name}' est en dehors de l'application '{app_path}'.\n"
                    f"- Chemin : '{found_path}'\n"
                )
                if not any(
                    file_name in error and "Fichier mal placé" in error
                    for error in errors
                ):
                    error_messages.append(error_message)
            else:
                error_message = (
                    f"\n❌ Fichier non trouvé ❌\n"
                    f"Le fichier '{file_name}' est introuvable dans '{app_path}' et '{project_root}'.\n"
                )
                if not any(
                    file_name in error and "Fichier non trouvé" in error
                    for error in errors
                ):
                    error_messages.append(error_message)

    errors.extend(error_messages)

    return updated_dict


def get_common_path(paths):
    if not paths:
        return ""
    return str(Path(os.path.commonpath(paths)))


def get_expected_path(file_paths, subfolder, file_name):
    file_paths = list(file_paths)
    if len(file_paths) == 1:
        common_path = str(Path(file_paths[0]).parent)
    else:
        common_path = get_common_path(file_paths)

    if subfolder == "layout" and file_name == "base.html":
        match = re.search(r"(.*?)(pages)", common_path)
    else:
        match = re.search(r"(.*?)(components|layout|sections)", common_path)

    if match:
        common_path = match.group(1)

    expected_path = Path(common_path) / subfolder / file_name

    return str(expected_path)
