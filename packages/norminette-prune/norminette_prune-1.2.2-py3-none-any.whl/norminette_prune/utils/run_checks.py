import sys
from pathlib import Path

from django.conf import settings

from norminette_prune.rules.content_python_file.check_basemodel_in_payloads import (
    check_basemodel_in_payloads,
)
from norminette_prune.rules.content_python_file.check_core_model_exists import (
    check_core_model_exists,
)
from norminette_prune.rules.content_python_file.check_core_model_usage import (
    check_core_model_usage,
)
from norminette_prune.rules.content_python_file.check_missing_str_method import (
    check_missing_str_method,
)
from norminette_prune.rules.content_python_file.check_textchoices_in_enums import (
    check_textchoices_in_enums,
)
from norminette_prune.rules.content_python_file.check_urls_name_parameter import (
    check_urls_name_parameter,
)
from norminette_prune.rules.content_python_file.check_view_function_naming import (
    check_view_function_naming,
)
from norminette_prune.rules.files_emplacement.check_pages_folder_structure import (
    check_pages_folder_structure,
)
from norminette_prune.rules.files_emplacement.check_templates_static_structure import (
    check_templates_static_structure,
)
from norminette_prune.rules.formate.normalize_django_tags_spacing import (
    normalize_django_tags_spacing,
)
from norminette_prune.rules.formate.remove_double_empty_lines import (
    remove_double_empty_lines,
)
from norminette_prune.rules.project_config.check_environment_class_in_settings import (
    check_environment_class_in_settings,
)
from norminette_prune.rules.project_config.check_for_envsettings_class_in_settings import (
    check_for_envsettings_class_in_settings,
)
from norminette_prune.rules.project_config.check_gitignore_content import (
    check_gitignore_content,
)
from norminette_prune.rules.project_config.check_pyproject_configuration import (
    check_pyproject_configuration,
)
from norminette_prune.rules.project_config.check_uv_use import check_uv_use
from norminette_prune.rules.project_config.check_valid_whitenoise_and_static_paths import (
    check_valid_whitenoise_and_static_paths,
)
from norminette_prune.rules.templates.check_component_and_layout_file_placement import (
    check_component_and_layout_file_placement,
)
from norminette_prune.rules.templates.check_svg_files_location_and_extension import (
    check_svg_files_location_and_extension,
)
from norminette_prune.rules.templates.check_svg_inclusion_paths import (
    check_svg_inclusion_paths,
)


def run_checks():
    errors_by_app = {}
    project_errors = []
    project_root = Path.cwd()

    try:
        check_uv_use(project_errors)
        check_pyproject_configuration(project_errors)
        check_for_envsettings_class_in_settings(project_errors)
        check_environment_class_in_settings(project_errors)
        check_valid_whitenoise_and_static_paths(project_errors)
        check_gitignore_content(project_errors)
        check_core_model_exists(project_errors)
        if project_errors:
            errors_by_app["__project__"] = project_errors

        for app in project_root.iterdir():
            if app.is_dir() and app.name in settings.INSTALLED_APPS:
                errors = []
                check_svg_files_location_and_extension(app.name, errors)
                check_svg_inclusion_paths(app.name, errors)
                check_view_function_naming(app.name, errors)
                check_core_model_usage(app.name, errors)
                check_textchoices_in_enums(app.name, errors)
                check_missing_str_method(app.name, errors)
                check_basemodel_in_payloads(app.name, errors)
                check_urls_name_parameter(app.name, errors)
                check_pages_folder_structure(app.name, errors)
                check_templates_static_structure(app.name, errors)
                check_component_and_layout_file_placement(app.name, errors)

                remove_double_empty_lines(app.name)
                normalize_django_tags_spacing(app.name)

                if errors:
                    errors_by_app[app.name] = errors

    except ValueError as e:
        print(f"Erreur lors de l'exécution des vérifications : {e}")
        sys.exit(1)

    return errors_by_app
