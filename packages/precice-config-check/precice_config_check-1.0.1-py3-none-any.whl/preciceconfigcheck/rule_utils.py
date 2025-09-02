import sys
import preciceconfigcheck.color as c


def rule_error_message(error: str) -> None:
    """
    This function is the generic shell for an error message, which will result in a system exit.
    It allows specifying an error which will be printed alongside the generic advice.
    :param error: The error which will get printed.
    """
    out: str = c.dyeing("[Error]", c.red) + " Exiting check."
    out += "\n" + error + "."
    out += "\nPlease run 'precice-tools check' for syntax errors."
    # Link to GitHub issue page
    out += (
        "\n\nIf you are sure this behaviour is incorrect, please leave a report at "
        + c.dyeing(
            "https://github.com/precice-forschungsprojekt/config-checker/issues", c.cyan
        )
    )
    sys.exit(out)


def format_list(items: list[str], conjunction: str = "and", sort: bool = True) -> str:
    """
    Formats a list of strings in a natural way, i.e. inserts commas and a conjunction at the end.
    :param items: strings to be concatenated
    :param conjunction: which conjunction to use, can be 'and' or 'or' for example.
    :param sort: set if the strings are to be sorted alphabetically.
    :return: concatenated string
    """
    if sort:
        items = sorted(items)

    if len(items) > 1:
        last_item = items.pop()
        padded_conjunction = " " + conjunction + " "

        return padded_conjunction.join([", ".join(items), last_item])
    elif len(items) == 1:
        return items[0]
    else:
        return ""
