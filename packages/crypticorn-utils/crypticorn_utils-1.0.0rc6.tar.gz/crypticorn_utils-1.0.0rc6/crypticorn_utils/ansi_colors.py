from enum import StrEnum


class AnsiColors(StrEnum):
    """Provides a collection of ANSI color codes for terminal text formatting, including regular, bright, and bold text colors. Useful for creating colorful and readable console output."""

    # Regular Text Colors
    BLACK = "\033[30m"  # black
    RED = "\033[31m"  # red
    GREEN = "\033[32m"  # green
    YELLOW = "\033[33m"  # yellow
    BLUE = "\033[34m"  # blue
    MAGENTA = "\033[35m"  # magenta
    CYAN = "\033[36m"  # cyan
    WHITE = "\033[37m"  # white

    # Bright Text Colors
    BLACK_BRIGHT = "\033[90m"  # black_bright
    RED_BRIGHT = "\033[91m"  # red_bright
    GREEN_BRIGHT = "\033[92m"  # green_bright
    YELLOW_BRIGHT = "\033[93m"  # yellow_bright
    BLUE_BRIGHT = "\033[94m"  # blue_bright
    MAGENTA_BRIGHT = "\033[95m"  # magenta_bright
    CYAN_BRIGHT = "\033[96m"  # cyan_bright
    WHITE_BRIGHT = "\033[97m"  # white_bright

    # Bold Text Colors
    BLACK_BOLD = "\033[1;30m"  # black_bold
    RED_BOLD = "\033[1;31m"  # red_bold
    GREEN_BOLD = "\033[1;32m"  # green_bold
    YELLOW_BOLD = "\033[1;33m"  # yellow_bold
    BLUE_BOLD = "\033[1;34m"  # blue_bold
    MAGENTA_BOLD = "\033[1;35m"  # magenta_bold
    CYAN_BOLD = "\033[1;36m"  # cyan_bold
    WHITE_BOLD = "\033[1;37m"  # white_bold

    # Reset Color
    RESET = "\033[0m"
