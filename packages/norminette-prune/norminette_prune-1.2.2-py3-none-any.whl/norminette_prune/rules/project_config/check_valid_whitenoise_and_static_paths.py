import re

from norminette_prune.rules.project_config.utils.read_settings import read_settings


def check_valid_whitenoise_and_static_paths(errors, current_dir=None):
    """
    Id: 13
    Description: Verify if WHITENOISE_ROOT and STATIC_ROOT have the correct paths.

    Tags:
        - configuration
        - content_settings

    Args:
        errors (list): A list to store error messages if the structure is incorrect.
    """

    whitenoise_regex = re.compile(
        r'WHITENOISE_ROOT\s*=\s*(os\.path\.join\(BASE_DIR,\s*["\']whitenoise_root["\']\)|BASE_DIR\s*/\s*["\']whitenoise_root["\'])'
    )
    static_root_regex = re.compile(
        r'STATIC_ROOT\s*=\s*(os\.path\.join\(BASE_DIR,\s*["\']static_root["\']\)|BASE_DIR\s*/\s*["\']static_root["\'])'
    )

    content = read_settings(errors, current_dir)

    if isinstance(content, list):
        return errors

    if not whitenoise_regex.search(content):
        errors.append(
            "Le fichier `settings.py` devrait contenir un chemin valide pour WHITENOISE_ROOT : "
            'WHITENOISE_ROOT = os.path.join(BASE_DIR, "whitenoise_root") ou '
            'WHITENOISE_ROOT = BASE_DIR / "whitenoise_root".'
        )

    if not static_root_regex.search(content):
        errors.append(
            "Le fichier `settings.py` devrait contenir un chemin valide pour STATIC_ROOT : "
            'STATIC_ROOT = os.path.join(BASE_DIR, "static_root") ou '
            'STATIC_ROOT = BASE_DIR / "static_root".'
        )
