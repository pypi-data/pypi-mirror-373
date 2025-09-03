import sys
from os import environ
from pathlib import Path

import django
from django.conf import settings

PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))


def initialize_django():
    """
    Vérifie si le projet Django est bien configuré en s'assurant que le fichier 'core/settings.py' existe.
    Initialise ensuite Django.

    Returns:
        bool: True si l'initialisation s'est bien passée, False sinon.
    """
    settings_path = PROJECT_ROOT / "core" / "settings.py"

    if not settings_path.exists():
        print(
            "🚨 Le fichier 'core/settings.py' est introuvable ! 🚨\n"
            "Assurez-vous d'exécuter cette commande depuis la racine de votre projet Django."
        )
        return False

    environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

    try:
        django.setup()
        settings.INSTALLED_APPS
        return True
    except ImportError:
        print("🚨 Erreur : Impossible d'importer les paramètres Django.")
        print("Vérifiez que votre module 'core.settings' est correct.")
        return False
    except AttributeError:
        print("🚨 Erreur : Les paramètres Django sont incorrects.")
        print("Vérifiez que INSTALLED_APPS est défini dans vos paramètres.")
        return False
    except Exception as e:
        print(f"🚨 Erreur lors de l'initialisation de Django : {e}")
        return False
