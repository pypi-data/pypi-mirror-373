def display_results(errors_by_app):
    """Affiche les résultats des vérifications."""
    if errors_by_app:
        print("\n🚨 Des erreurs ont été détectées 🚨\n")
        if "__project__" in errors_by_app:
            print(
                "----------------------------\n\n🔧 Voici les erreurs de configuration pour votre projet django :\n"
            )
            for error in errors_by_app["__project__"]:
                print(f"📌 {error}\n")
            del errors_by_app["__project__"]
        for app, errors in errors_by_app.items():
            print(f"----------------------------\n\n🔍 Application : `{app}`\n")
            for error in errors:
                print(f"---------------------------- {error}\n")
    else:
        print("✅ Aucune erreur détectée dans votre Django. 🎉👏")
