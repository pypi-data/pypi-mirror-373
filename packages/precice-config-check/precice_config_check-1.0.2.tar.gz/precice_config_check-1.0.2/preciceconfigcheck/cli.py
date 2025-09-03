import argparse
import sys
import pathlib

from preciceconfigcheck.severity import Severity
import preciceconfigcheck.color as c

from precice_config_graph import graph as g, xml_processing

from preciceconfigcheck.rules_processing import check_all_rules, print_all_results


def runCheck(path: pathlib.Path, debug: bool):
    if debug:
        print(f"[{Severity.DEBUG.value}]: Debug mode enabled")

    if path.name.endswith(".xml"):
        print(f"Checking '{c.dyeing(str(path), c.cyan)}' for logical issues...")
    else:
        print(
            f"[{Severity.ERROR.value}]: '{c.dyeing(str(path), c.cyan)}' is not an xml file",
            file=sys.stderr,
        )
        return 1

    # Step 1: Use preCICE itself to check for basic errors
    # TODO: Participant.check(...)

    # Step 2: Detect more issues through the use of a graph
    root = xml_processing.parse_file(path)
    graph = g.get_graph(root)

    # Individual checks need the graph
    violations_by_rule = check_all_rules(graph, debug)

    # if the user uses severity=debug, then the severity has to be passed here as an argument
    print_all_results(violations_by_rule, debug)

    if all(map(lambda vals: len(vals) == 0, violations_by_rule.values())):
        return 0
    else:
        return 2


def main():
    parser = argparse.ArgumentParser(
        usage="%(prog)s",
        description="Checks a preCICE config.xml file for logical errors.",
    )
    parser.add_argument(
        "src", type=pathlib.Path, help="Path of the config.xml source file."
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enables debug mode")
    args = parser.parse_args()

    return runCheck(path=args.src, debug=args.debug)


if __name__ == "__main__":
    sys.exit(main())
