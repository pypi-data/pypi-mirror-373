import textwrap

from norminette_prune.utils.rules.extract_rules import (
    get_sorted_rules,
    get_tags_descriptions,
)


def display_rules_terminal():
    """
    Print rule in terminal
    """
    docstrings = get_sorted_rules()
    tags_descriptions = get_tags_descriptions()

    print(
        "\n\033[1m================================================ Norminette Rules ================================================\033[0m\n"
    )

    print(
        "\033[1m{:<5} {:<30} {:<60} {:<20}\033[0m".format(
            "ID", "Name", "Description", "Tags"
        )
    )

    print("-" * 115)

    for function_name, rule_id, description, tags in docstrings:
        print("\n")
        wrapped_description = textwrap.wrap(description, width=57)

        first_line = wrapped_description[0] if wrapped_description else ""
        print(
            "{:<5} {:<30} {:<60} {:<20}".format(
                rule_id, function_name, first_line, tags
            )
        )

        for extra_line in wrapped_description[1:]:
            print("{:<5} {:<30} {:<60} {:<20}".format("", "", extra_line, ""))

    print("\n\n\033[1mTags:\033[0m")
    for tag, description in tags_descriptions.items():
        print(f"  \033[1m{tag}\033[0m: {description}")
    print()
