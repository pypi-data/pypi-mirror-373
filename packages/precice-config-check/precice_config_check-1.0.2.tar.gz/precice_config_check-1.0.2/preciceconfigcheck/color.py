black: str = "\033[1;30m"
red: str = "\033[1;31m"
green: str = "\033[1;32m"
yellow: str = "\033[1;33m"
blue: str = "\033[1;34m"
purple: str = "\033[1;35m"
cyan: str = "\033[1;36m"
white: str = "\033[1;37m"
reset: str = "\033[0m"


def dyeing(string: str, color: str) -> str:
    return f"{color}{string}{reset}"
