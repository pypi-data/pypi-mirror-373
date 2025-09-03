import json
import re
import urllib.request
from pathlib import Path

from norminette_prune.utils.rules.extract_rules import (
    get_sorted_rules,
    get_tags_descriptions,
)


def translate_text(text):
    """
    Translate with 'libre translate'
    """
    try:
        url = "https://translate.fedilab.app/translate"

        data = {"q": text, "source": "en", "target": "fr", "format": "text"}

        encoded_data = json.dumps(data).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(
            url, data=encoded_data, headers=headers, method="POST"
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            response_data = response.read().decode("utf-8")
            result = json.loads(response_data)
            return result.get("translatedText", text)
    except Exception as e:
        print(f"Erreur de traduction: {e}")
        return text


def update_readme_file(filename: Path, rules_markdown: str, is_french: bool = False):
    """Update Readme with rules and tags"""
    if not filename.exists():
        print(f"⚠️ Warning: {filename} not found.")
        return

    content = filename.read_text(encoding="utf-8")

    pattern = r"## Règles.*?(?=##|\Z)" if is_french else r"## Rules.*?(?=##|\Z)"
    content = re.sub(pattern, "", content, flags=re.DOTALL)

    tags_pattern = r"### Tags.*?(?=##|\Z)"
    content = re.sub(tags_pattern, "", content, flags=re.DOTALL)

    content = content.rstrip("\n") + "\n" + rules_markdown

    filename.write_text(content, encoding="utf-8")


def generate_english_readme():
    """Generate and update English README"""
    docstrings = get_sorted_rules()
    tags_descriptions = get_tags_descriptions()

    rules_markdown = "## Rules\n\n"
    rules_markdown += "| Id  | Name | Description | Tags |\n"
    rules_markdown += "|:---:|-----|-------------|------|\n"

    for function_name, rule_id, description, tags in docstrings:
        rules_markdown += f"| {rule_id} | {function_name} | {description} | {tags} |\n"

    rules_markdown += "\n\n### Tags  \n"

    for tag, description in tags_descriptions.items():
        rules_markdown += f"- **{tag}** : {description}\n"

    update_readme_file(Path("README.md"), rules_markdown)


def generate_french_readme():
    """Generate and update French README with translation"""
    docstrings = get_sorted_rules()
    tags_descriptions = get_tags_descriptions()

    rules_markdown = "## Règles\n\n"
    rules_markdown += "| Id  | Nom | Description | Tags |\n"
    rules_markdown += "|:---:|-----|-------------|------|\n"

    for function_name, rule_id, description, tags in docstrings:
        try:
            translated_description = translate_text(description)
        except Exception as e:
            print(f"❌ Erreur lors de la traduction de la règle {rule_id}: {e}")
            translated_description = description

        rules_markdown += (
            f"| {rule_id} | {function_name} | {translated_description} | {tags} |\n"
        )

    rules_markdown += "\n\n### Tags  \n"

    for tag, description in tags_descriptions.items():
        try:
            translated_tag_desc = translate_text(description)
        except Exception as e:
            print(f"❌ Erreur lors de la traduction du tag {tag}: {e}")
            translated_tag_desc = description

        rules_markdown += f"- **{tag}** : {translated_tag_desc}\n"

    update_readme_file(Path("README-FR.md"), rules_markdown, True)


def update_readme_files():
    """Updates both README.md and README-FR.md with current rules."""
    generate_english_readme()
    generate_french_readme()


update_readme_files()
