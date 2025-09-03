# Prune's Norminette

## What is it for?

The norminette automatically checks the organization of files in a Django project as well as code rules.
This allows for the same code standard between projects and makes it easier to navigate.

## Prerequisites

- To be installed on a Prune Django project that uses poetry or UV

## UV project

### Installation

Run the following command in the console:

```bash
uv add norminette_prune
```

### Running the norminette

To run the package, simply enter in the console:
```bash
norminette_prune
```

### Display rules in the project

To list all the rule checks in the project, run the following command:
```bash
norminette_display_rules
```

### Updating the norminette
Don't hesitate to regularly run `uv sync --upgrade`, as the norminette evolves with time and our practices!

## Poetry project

### Installation

Run the following command:

```bash
poetry add norminette_prune
```

### Running the norminette
```bash
poetry run norminette_prune
```

### Display rules in the project

To list all the rule checks in the project, run the following command:
```bash
poetry run norminette_display_rules
```

### Updating the norminette
Don't hesitate to regularly run `poetry update`, as the norminette evolves with time and our practices!

## For developers: add new rule

The rules are located in the `rules/` folder.

To add a new rule based on a function's docstring, follow this format:
```python
"""
    Id: 10
    Description: Describe what the rule checks.

    Tags:
        - Use relevant tags from the list below.

    Args:
        app (str): The name of the Django app to check.
        errors (list): A list to store error messages if the structure is incorrect.
"""
```

### Available Tags
The currently available tags are:

- **web_files**: HTML, JS, and CSS files.
- **python_files**: Python files with `.py` extension.
- **architecture**: Checks folder and file placement consistency.
- **format**: Directly modifies file formatting.
- **files_content**: Inspects file contents.

### Integration Steps
- Import the new function in `utils/run_checks.py`. (Remember to add errors in args)
- Sync the new rules to update `README.md` and `README-FR.md`.

To sync rules after adding them to the project, run:
```bash
python -m norminette_prune.utils.rules.generate_readme
```

For adding a tag, add it to the `get_tags_descriptions()` function in `utils/rules/extract_rules.py` file.

## Project architecture at Prune

To access the documentation, please go to the link where you can find documentation in English and French.

[Documentation](https://gitlab.com/bastien_arnout/prune-doc.git)

If you want to download it directly, here is the link:

[Download](https://gitlab.com/bastien_arnout/prune-doc/-/archive/main/prune-doc-main.zip)

# Available Versions

| Version | Date       | Notes                      |
|---------|-----------|---------------------------|
| 0.1.0   | 2025-03-13 | Initial release  |
| 0.1.1   | 2025-03-14 | Fixed import bug and added rules      |
| 1.0.0   | 2025-03-14 | Added rules to readme            |
| 1.1.0   | 2025-03-17 | added command to display rules on terminal            |
| 1.2.0   | 2025-03-28 | Improved compatibility, added checks, and fixed issues   |
## Rules

| Id  | Name | Description | Tags |
|:---:|-----|-------------|------|
| 01 | check_view_function_naming | Verify that the name of rendering functions for views ends with '_view'. | python_files files_content |
| 02 | check_pages_folder_structure | Verify if `page.html` files are inside the `pages/` folder and ensure files in `pages/`     are named `page` (except in `components`, `sections`, and `layouts` folders). | web_files architecture |
| 03 | check_templates_static_structure | Verify that the `static/` and `templates/` folders contain only one subfolder named after the app. | architecture |
| 04 | remove_double_empty_lines | Remove double empty lines in HTML, JS, and CSS files. | format files_content web_files |
| 05 | normalize_django_tags_spacing | Normalize spaces in Django tags (with exactly one space between the tag and its content). | format web_files files_content |
| 06 | check_component_and_layout_file_placement | Verify that layout, component, and section files are correctly placed based on their `include` references. | web_files architecture |
| 07 | check_svg_inclusion_paths | Ensure that SVG includes use absolute paths. | web_files files_content |
| 08 | check_svg_files_location_and_extension | Verify that SVG files are inside the `svg/` folder and use the `.html` extension. | web_files architecture |
| 09 | check_uv_use | Verify if UV is used in the project by checking for 'uv.lock' in the current directory or subdirectories. | configuration |
| 10 | check_pyproject_configuration | Verify if pyproject.toml exist and contain pydantic, ipython and whitenoise | configuration |
| 11 | check_for_envsettings_class_in_settings | Verify if class EnvSettings exists in `settings.py` | configuration content_settings |
| 12 | check_environment_class_in_settings | Verify if class Environment exists in `settings.py` | configuration content_settings |
| 13 | check_valid_whitenoise_and_static_paths | Verify if WHITENOISE_ROOT and STATIC_ROOT have the correct paths. | configuration content_settings |
| 14 | check_gitignore_content | Verify if ".env", ".venv", "__pycache__/", "node_modules/" and "static_root" are in `.gitignore` file | configuration |
| 15 | check_core_model_usage | Checks if a model directly inherits from other than CoreModels. | python_files files_content |
| 16 | check_core_model_exists | Checks if a core model class exists in lib/models.py | python_files files_content |
| 17 | check_textchoices_in_enums | Checks if TextChoices classes are defined in a file named 'enums.py'. | python_files files_content |
| 18 | check_missing_str_method | Checks if '__str__' method is present on `models.py`. | python_files files_content |
| 19 | check_urls_name_parameter | Checks if all URL patterns in urls.py have a 'name' parameter. | python_files files_content |
| 20 | check_basemodel_in_payloads | Checks if BaseModel (Pydantic) classes are defined in a file named 'payloads.py'. | python_files files_content |


### Tags  
- **web_files** : HTML, JS, and CSS files.
- **python_files** : Python files with `.py` extension.
- **architecture** : Checks folder and file placement consistency.
- **format** : Directly modifies file formatting.
- **files_content** : Inspects file contents.
- **configuration** : Verify project configuration.
- **content_settings** : Verify settings.py configuration.
