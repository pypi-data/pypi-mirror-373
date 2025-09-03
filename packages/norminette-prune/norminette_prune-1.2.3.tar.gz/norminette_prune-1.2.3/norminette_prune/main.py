from norminette_prune.utils.display_result import display_results
from norminette_prune.utils.run_checks import run_checks
from norminette_prune.utils.setup_django import initialize_django


def main():
    if not initialize_django():
        return

    errors = run_checks()

    display_results(errors)


if __name__ == "__main__":
    main()
