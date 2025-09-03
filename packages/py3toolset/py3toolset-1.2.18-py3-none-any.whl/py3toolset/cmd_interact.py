"""
Functions to help writing user interactions with a script (parsing options,
yes/no question interactions, etc.).
"""

import re


def is_help_switch(string):
    """
    Tests if string is a -h/--help switch.

    Args:
        string: str
            String to test.

    Return:
        - True if the string is a help switch: -h or --help.
        - False otherwise.

    Example:
        >>> is_help_switch('-h')
        True
        >>> is_help_switch('--help')
        True
        >>> is_help_switch('-a')
        False
        >>> is_help_switch('--anything')
        False
        >>> is_help_switch('anything')
        False

    """
    return is_switch("h", "help", string)


def contains_help_switch(strings):
    """
    Tests if strings contain a -h/--help switch.

    strings: list[str]
        strings to tests.

    Return:
        - True if strings contain a help switch: -h/--help.
        - False otherwise.

    Examples:
        >>> contains_help_switch(["-h", "--anything"])
        True
        >>> contains_help_switch(["--help", "anything"])
        True
        >>> contains_help_switch(["-a", "--anything"])
        False
    """
    return contains_switch("h", "help", strings)


def is_switch(short_sw, long_sw, string):
    """
    Tests if string is the switch short_sw or long_sw.

    Args:
        short_sw: str
            short switch (e.g. '-s').
        long_sw:
            long switch (e.g. '--switch').
        string: str
        string to test.

    Return:
        - True if string is the short or long switch defined in 2 first args.
        - False otherwise.

    Examples:
        >>> is_switch("h", "help", "-h")
        True
        >>> is_switch("h", "help", "--help")
        True
        >>> is_switch("h", "help", "-z")
        False
        >>> is_switch("h", "help", "--zip")
        False

    """
    return (short_sw and re.match("^(-" + short_sw + ")$", string) is not None
            or
            long_sw and re.match("^(--" + long_sw + ")$", string) is not None)


def contains_switch(short_sw, long_sw, strings):
    """
    Tests if a switch short_sw or long_sw belongs to one of strings.

    Args:
        short_sw: str
            short switch (e.g. '-s').
        long_sw:
            long switch (e.g. '--switch').
        strings: list[str]
            strings to tests.

    Return:
        - True if any strings[i] verifies:
            ``is_switch(short_sw, long_sw, strings)``,
        - False otherwise.

    Examples:
        >>> contains_switch("h", "help", ["-h","-a"])
        True
        >>> contains_switch("h", "help", ["--zip","-a"])
        False

    """
    for i in range(0, len(strings)):
        if is_switch(short_sw, long_sw, strings[i]):
            return True
    else:
        return False


def ask_yes_or_no(answer=""):
    """
    Asks user 'yes' or 'no' and loops until a valid response is given.

    The response can also be 'y' or 'n'.

    Args:
        answer: str
            If set to a valid response, the user is not asked for an answer.

    Return:
        The answer.

    Examples:
        >>> ask_yes_or_no('y')
        'y'
        >>> ask_yes_or_no('yes')
        'yes'
        >>> ask_yes_or_no('no')
        'no'
        >>> ask_yes_or_no('n')
        'n'
        >>> # with a user input
        >>> # ask_yes_or_no()
        # [y/n or yes/no]: y
        # 'y'

    """
    while re.match("^(y|yes|n|no)$", answer, re.I) is None:
        print("[y/n or yes/no]: ", end='')
        answer = input()
    return answer
