import re

from norminette_prune.rules.project_config.utils.read_settings import read_settings


def check_environment_class_in_settings(errors, current_dir=None):
    """
    Id: 12
    Description: Verify if class Environment exists in `settings.py`

    Tags:
        - configuration
        - content_settings

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """
    class_regex = re.compile(
        r"class\s+Environment\s*\(\s*(?:Enum\s*,\s*str|str\s*,\s*Enum)\s*\)\s*:"
    )
    content = read_settings(errors, current_dir)

    if isinstance(content, list):
        return errors
    if not class_regex.search(content):
        errors.append(
            "Le fichier 'settings.py' devrait contenir une classe 'Environment' qui permet d'énumérer les variables d'environnement."
        )
