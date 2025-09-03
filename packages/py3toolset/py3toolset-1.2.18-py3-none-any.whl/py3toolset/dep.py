"""
Dependency checking module.
"""

import os
from os.path import exists
import sys


checked_progs = []


def check_executable(progname, *extra_paths, info_msg=""):
    """
    Checks if the program ``progname`` availability.

    The program is search in PATH environment variable and optionally extra
    paths.
    If the program is not found an exception is raised.

    If a program has already been checked before it is stored in module
    variable ``checked_progs`` and next calls to ``check_executable`` will
    always succeed.

    Args:
        progname: ``str``
            program name to check the availability.
        extra_paths: ``list[str]``
            extra paths to find the program in.
        info_msg: ``str``
            a message to display if the function failed to find the program.

    Return:
        None in case of success (program found).
        Exception raise otherwise.


    Example:
        >>> check_executable('more')
        >>> info_msg = 'more not found'
        >>> check_executable('more', None, info_msg)
        >>> check_executable('more', '/', 'home', info_msg)
    """
    if _prog_already_checked(progname):  # work already done
        return
    if extra_paths is not None:
        for p in extra_paths:
            # don't add a path twice in PATH
            if p not in os.environ["PATH"].split(os.pathsep):
                print("Adding: "+repr(p)+" TO PATH ENV.")
                os.environ["PATH"] = p+os.pathsep+os.environ["PATH"]
    probed_pathes = [os.path.join(path.strip('"'), progname)
                     for path in os.environ["PATH"].split(os.pathsep)]
    existing_pathes = [path for path in probed_pathes if exists(path)]
    if len(existing_pathes) == 0:
        raise Exception("Error: " + progname + " not found in PATH environment"
                        " variable directories.\n"+info_msg)
    executable_pathes = [path for path in existing_pathes
                         if os.access(path, os.X_OK)]
    if len(executable_pathes) == 0:
        raise Exception("Error: " + progname + " found but not executable "
                        + repr(existing_pathes))
    # print("exec pathes: " + repr(executable_pathes))
    checked_progs.append(progname)


def check_prog_deps(prog_list, *extra_paths, info_msgs=None):
    """
    Checks the availability of programs in ``prog_list``.

    It is just an helper function that uses :func:`.check_executable`.

    Args:
        prog_list: ``list[str]``
            programs to check availability.
        extra_paths: ``list[str]``
            paths to search the programs in addition to the paths in PATH
            environment variable.
        info_msgs: ``list[str]``
            Messages to display when the function failed to find a program.
            One message per program or none at all.
            The order must match order of ``prog_list``.


    Return:
        None in case of success (program found).
        Exception raise otherwise.

    Example:
        >>> check_prog_deps(['more', 'dir'])
        >>> info_msgs = [['more not found'], ['dir not found']]
        >>> check_prog_deps(['more', 'dir'], None, info_msgs)
        >>> check_prog_deps(['more', 'dir'], '/', '/home', info_msgs)
    """
    if info_msgs is not None:
        for progname, info in zip(prog_list, info_msgs):
            check_executable(progname, *extra_paths, info_msg=info)
    else:
        for progname in prog_list:
            check_executable(progname, *extra_paths)


def _prog_already_checked(progname):
    """
    Returns ``True`` if a program has already been found ``False`` otherwise.

    """
    return checked_progs.count(progname) > 0


def check_mod_pkg(mod_pkg, message=None, stdout=False):
    """
    Checks Python module/package availability.

    Args:
        mod_pkg: ``str``
            Python package or module name (including Cython extension module).
        message: ``str``
            Error message displayed the module/package has not been found.
        stdout: ``bool``
            If ``True`` display ``message`` on ``sys.stdout``,
            otherwise on ``sys.stderr`` (default).

    Return:
        ``True`` if Python ``mod_pkg`` (module or package) is found.
        ``False`` otherwise.
        ``None`` if ``mod_pkg`` wasn't found but not because of an
        ``ImportError``.

    Example:
       >>> check_mod_pkg("notexistingpkg", "pkg not found.", stdout=True)
       pkg not found.
       False
       >>> check_mod_pkg("os.path", "it must be found")
       True

    """
    try:
        exec('import '+mod_pkg)
        return True
    except ImportError:
        if message is not None:
            print(message, file=sys.stdout if stdout else sys.stderr)
        return False
