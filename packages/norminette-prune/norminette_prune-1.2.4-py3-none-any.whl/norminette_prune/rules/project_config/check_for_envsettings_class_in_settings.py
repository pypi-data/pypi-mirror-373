import re

from norminette_prune.rules.project_config.utils.read_settings import read_settings


def check_for_envsettings_class_in_settings(errors, current_dir=None):
    """
    Id: 11
    Description: Verify if class EnvSettings exists in `settings.py`

    Tags:
        - configuration
        - content_settings

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
        current_dir (Path, optional): Directory to search for settings.py. Defaults to current working directory.
    """

    class_regex = re.compile(r"class\s+EnvSettings\s*\(\s*BaseSettings*\s*\)\s*:")

    content = read_settings(errors, current_dir)
    if isinstance(content, list):
        return errors

    if not class_regex.search(content):
        errors.append(
            "Le fichier 'settings.py' devrait contenir une classe 'EnvSettings' qui permet de parser les variables d'environnement."
        )
