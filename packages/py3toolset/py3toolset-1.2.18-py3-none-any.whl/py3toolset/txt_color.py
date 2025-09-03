"""
Module to print colored text in a terminal.
"""
import shutil


class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


class Style:
    BOLD = "\033[1m"


def col(col, txt):
    """
    Colorizes txt using ANSI escape code (encoded in :class:`.Color`).

    Args:
        col: ``int``
            ``Color.RED``, ``Color.GREEN``, ``Color.YELLOW``, ``Color.BLUE``.
        txt: ``str``
            the txt to colorize.

    Return:
        ``txt`` encoded in ``col`` color.

    """
    if col not in [Color.BLUE, Color.YELLOW, Color.GREEN, Color.RED]:
        raise Exception("Not valid color")
    return col + txt.replace(Color.END, Color.END+""+col) + Color.END


def frame(title, col=Color.BLUE, centering=True):
    """Frames the text ``title`` in color.

    The enclosing frame is made of colored dash characters.

    Args:
        title: ``str``
            The text to frame.
        col: ``int``
            ``Color.RED``, ``Color.GREEN``, ``Color.YELLOW``, ``Color.BLUE``
            (default).
        centering: ``bool``
            ``True`` (default) for centered ``title`` in terminal,
            ``False`` otherwise.

    Return:
        ``title`` encoded in ``col`` color with dash characters above and
        below.
    """
    return (col + "-"*get_width() + "\n" +
            Style.BOLD+(centering and center(title) or title) + "\n" +
            Color.END + col + "-"*get_width() + Color.END)


def big_frame(title, col=Color.RED, centering=True):
    """Frames the text ``title`` in color.

       Same as :func:`.frame` but text in red by default with enclosing frame
       made of ``=`` characters.
    """
    return (col + "="*get_width() + "\n" +
            Style.BOLD+(centering and center(title) or title) + "\n" +
            Color.END + col + "="*get_width() + Color.END)


def center(txt):
    """Centers a text according to the terminal number of columns.

    The centering is made by space insertions.

    Return:
        The centered text of ``txt``.
    """
    return " "*((get_width() - len(txt)) // 2) + txt


def print_center(txt):
    """ Centers and prints text ``txt``.

    .. seealso::
        :func:`.center`
    """
    print(center(txt))


def print_frame(title, col=Color.BLUE, centering=True):
    """Prints ``title`` enclosed in frame (dash characters).

    .. seealso::
        :func:`.frame`
    """
    print(frame(title, col, centering))


def get_width():
    "Gets the terminal number of columns."
    return shutil.get_terminal_size()[0]


def print_big_frame(title, col=Color.RED, centering=True):
    """Prints ``title`` enclosed in big frame (``=`` characters).

    .. seealso::
        :func:`.big_frame`
    """
    print(big_frame(title, col, centering))


def bold(txt):
    "Returns txt in bold style (for terminal display)"
    return Style.BOLD + txt + Color.END


def warn(msg):
    "Formats and print ``msg`` as a warning message (prefix 'WARNING:' in red)"
    print(col(Color.RED, "WARNING: ")+msg)


def err(msg):
    """Formats a msg as an error message.

    Format: prefix 'Error:' in bold style and all message in red.
    """
    if not msg.lower().startswith("error"):
        msg = bold("Error: ") + msg
    print_frame(msg, Color.RED, centering=False)


def red(txt):
    """
    Returns ``txt`` as red ``str`` (see ``col``).
    """
    return col(Color.RED, txt)


def green(txt):
    """
    Returns ``txt`` as green ``str`` (see ``col``).
    """
    return col(Color.GREEN, txt)


def blue(txt):
    """
    Returns ``txt`` as blue ``str`` (see ``col``).
    """
    return col(Color.BLUE, txt)


def yellow(txt):
    """
    Returns ``txt`` as yellow ``str`` (see ``col``).
    """
    return col(Color.YELLOW, txt)


# def alias color functions
r = red
g = green
b = blue
y = yellow
