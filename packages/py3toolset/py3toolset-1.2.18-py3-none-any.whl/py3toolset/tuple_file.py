"""
Module for conversion of list of tuples <-> text file.

This module is mostly to use to avoid:

- use of ``numpy.savetxt``/``loadtxt``,
- and NumPy array to list-of-tuples conversion.
"""
from os.path import exists


def tuples2file(tuple_list, tfile, format_str='', overwrite=False):
    """
    Converts ``tuple_list`` into a text file ``tfile``.

    Each tuple occupies one line.
    One column is added in file for each tuple element.

    For example, the tuple list [(x1,y1,z1,w1), (x2,y2,z2,w2)]
    is converted to the following file lines:
    x1 y1 z1 w1
    x2 y2 z2 w2

    Args:
        tuple_list: ``list[tuple]``
            The list of tuples to write as in file.
        tfile: ``str``
            Output filepath.
        format_str: ``str``
            if specified is used as a line format string to the data in tuple.
            See example below.

            .. warning::
                The function doesn't check the format string validity.
        overwrite: ``bool``
            - ``True``: a preexisting file is overwritten.
            - ``False`` (default): if file preexists an exception is raised.

    Example:
        >>> import os
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> output = "t2f_out-" + rand_suffix
        >>> xy_tuples = [(1, 456.), (2, 789), (3, 111213)]
        >>> tuples2file(xy_tuples, output, format_str="{0:1d}={1:3.1f}")
        >>> # output is then:
        >>> f = open(output)
        >>> for line in f.readlines(): print(line, end='')
        1=456.0
        2=789.0
        3=111213.0
        >>> f.close()
        >>> # delete file
        >>> os.unlink(output)

    """
    if exists(tfile) and not overwrite:
        raise Exception("Error tuples2file(): file "+tfile+" already exists.")
    f = open(tfile, "w")
    for t in tuple_list:
        if format_str:
            if not format_str.endswith("\n"):
                format_str += "\n"
            f.write(str(format_str).format(*t))
        else:
            f.write(" ".join([str(e) for e in t])+"\n")
    f.close()


def file2tuples(tfile, tuple_list=None):
    """
    Converts a file ``tfile`` organized in columns to a list of tuples.

    Returns a list of tuples (one tuple per line of file).
    The elements in file as taken as float numbers.

    Args:
        tfile: ``str``
            input filepath.
        tuple_list: ``list[tuple]``
            The output list of tuples. Defaultly ``None``.

    Return:
        tuple list corresponding to ``tfile`` input.

    Example:
        >>> import os
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> output = "t2f_out-" + rand_suffix
        >>> in_tuples = [(1, 456.), (2, 789), (3, 111213)]
        >>> tuples2file(in_tuples, output)
        >>> # output is then:
        >>> out_tuples = file2tuples(output)
        >>> print(out_tuples)
        [(1.0, 456.0), (2.0, 789.0), (3.0, 111213.0)]
    """
    if tuple_list is None:
        tuple_list = []
    f = open(tfile)
    for line in f:
        tuple_list.append(tuple([float(n) for n in line.strip().split()]))
    f.close()
    return tuple_list
