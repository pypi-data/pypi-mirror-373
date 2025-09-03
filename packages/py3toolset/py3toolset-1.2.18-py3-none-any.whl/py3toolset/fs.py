"""
A module for file system operations.

File removal, copying, checking, path operations, etc.
"""

from glob import glob
from os.path import (isabs, exists, os, dirname, basename, isfile, isdir, join,
                     sep)
from os import environ, pathsep, mkdir
import re
import sys
from posix import remove, getcwd, rmdir
from shutil import which, copyfile


def remove_files(*files):
    """
    Removes all ``files`` from the file system.

    .. note::
        Item which is not a file is ignored.

    .. seealso::
        :func:`.remove_dirs`

    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> # create a folder and dummy files
        >>> parent_dir = "test_remove_files" + rand_suffix
        >>> os.mkdir(parent_dir)
        >>> f1 = os.path.join(parent_dir, "f1")
        >>> f_out = open(f1, 'w')
        >>> f_out.writelines(["Test test test"])
        >>> f_out.close()
        >>> f2 = os.path.join(parent_dir, "f2")
        >>> f2_out = open(f2, 'w')
        >>> f2_out.writelines(["Test2 test2 test2"])
        >>> f2_out.close()
        >>> os.path.exists(f1)
        True
        >>> os.path.exists(f2)
        True
        >>> # remove files f1 and f2
        >>> remove_files(f1, f2)
        >>> os.path.exists(f1)
        False
        >>> os.path.exists(f2)
        False
        >>> remove_dirs(parent_dir)

    """
    for f in files:
        if isfile(f):
            remove(f)


def remove_dirs(*dirs):
    """
    Removes recursively directories/folders.

    Args:
        dirs: ``list``
            List of directories to remove.

    .. note::
        If an element in dirs isn't a folder, it is ignored.

    .. seealso::
        :func:`.remove_files`


    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> # create a folder and dummy files
        >>> parent_dir = "test_remove_dirs" + rand_suffix
        >>> parent_dir2 = "test_remove_dirs" + rand_suffix + '2'
        >>> os.mkdir(parent_dir)
        >>> os.mkdir(parent_dir2)
        >>> f1 = os.path.join(parent_dir, "f1")
        >>> f_out = open(f1, 'w')
        >>> f_out.close()
        >>> f2 = os.path.join(parent_dir, "f2")
        >>> f2_out = open(f2, 'w')
        >>> f2_out.close()
        >>> os.path.exists(f1)
        True
        >>> os.path.exists(f2)
        True
        >>> os.path.exists(parent_dir2)
        True
        >>> # remove directories
        >>> remove_dirs(parent_dir, parent_dir2)
        >>> os.path.exists(parent_dir)
        False
        >>> os.path.exists(parent_dir2)
        False

    """
    for d in dirs:
        if isdir(d):
            for e in glob(d+os.sep+"*"):
                if isdir(e):
                    remove_dirs(e)
                else:
                    remove_files(e)
            # d empty
            rmdir(d)


def get_prog_parent_dir():
    """
    Returns absolute path of parent folder of the currently running script.

    Example:

        Script ``./nop.py``:

        .. code-block:: python

           #!/usr/bin/env python3
           from py3toolset.fs import get_prog_parent_dir

           if __name__ == '__main__':
               print(get_prog_parent_dir())

        Use of script and function:

        .. code-block:: bash

           $ echo $PWD
           /my/current/working/dir/.
           $ ./nop.py
           /my/current/working/dir
           $ export PATH=$PATH:.
           $ nop.py
           /my/current/working/dir/.
           $ cd ..
           $ ./dir/nop.py
           /my/current/working/dir


    """
    pdir = dirname(sys.argv[0])
    if pdir.startswith(os.sep):
        # absolute path of prog was given
        return pdir
    elif not pdir:
        # no parent dir given in script cmd
        # prog probably located through PATH
        return which(sys.argv[0]) or "."
        # TODO: or "." should be removed
        # it was just a tmp test trick
        # anyway it shouldn't be reached
    else:
        # relative dir given to script
        # return absolute dir
        return getcwd() + os.sep + pdir


def set_abs_or_relative_path(parent_dir, _file):
    """
    Sets a full path for ``_file`` (can be relative or absolute).

    If ``_file`` is an absolute path returns ``_file`` as is.
    Otherwise if ``parent_dir`` is set, returns the path ``parent_dir/_file``.
    Raises an exception if ``parent_dir`` is ``None`` while ``_file`` is not
    absolute.
    The function never verifies the file exists, it only builds a full path.

    Args:
        parent_dir: ``str``
            a candidate parent directory (relative or absolute path)
            for _file. It is only used if _file is not an absolute path.
        _file: ``str``
            any filename or filepath (relative to ``parent_dir`` or
            ``absolute``).

    Return:
        the full (absolute or relative path) of ``_file``; that is
        ``parent_dir + os.sep + _file`` or ``_file``.

    Example:
        >>> set_abs_or_relative_path(None, '/my/absolute/file/path')
        '/my/absolute/file/path'
        >>> set_abs_or_relative_path('/my/absolute/file', 'path')
        '/my/absolute/file/path'
        >>> set_abs_or_relative_path(None, 'path')
        Traceback (most recent call last):
        ...
        ValueError: parent_dir must be defined

    """
    if isabs(_file):
        # _file is absolute path
        # or not absolute path, but exists
        return _file
    elif parent_dir is None:
        raise ValueError('parent_dir must be defined')
    else:  # parent_dir is not None:  # not abs path, prefix with parent dir
        return parent_dir + os.sep + _file


def all_files_in_same_dir(*files):
    """
    Returns ``True`` all ``files`` are in the same folder, ``False`` otherwise.

    Example:
        >>> all_files_in_same_dir('/etc/hosts', '/etc/passwd')
        True
        >>> all_files_in_same_dir('/etc/hosts', '/etc/passwd', '/usr/share')
        False

    """
    pdir = None
    for f in files:
        if pdir is None:
            pdir = dirname(f) or "."
        elif not exists(pdir + os.sep + basename(f)):
            return False
    return True


def glob_files(*files, only_first=True):
    """
    Helper to do a :func:`glob` on each file pattern in ``files``.

    Args:
        only_first: ``bool``
            If ``True`` (default) returns only the first file matching pattern
            ``files[i]`` for all ``i`` otherwise (``False``) returns all of
            them.
    Return:
        the list of "globbed" files.

    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> # create a folder and dummy files
        >>> dir = "test_remove_dirs" + rand_suffix
        >>> dir2 = "test_remove_dirs" + rand_suffix + '2'
        >>> os.mkdir(dir)
        >>> os.mkdir(dir2)
        >>> f1 = os.path.join(dir, "f1")
        >>> f_out = open(f1, 'w')
        >>> f_out.close()
        >>> f2 = os.path.join(dir, "f2")
        >>> f2_out = open(f2, 'w')
        >>> f2_out.close()
        >>> f3 = os.path.join(dir2, "f3")
        >>> f3_out = open(f3, 'w')
        >>> f3_out.close()
        >>> # globbing onfly first file of each globbing
        >>> files = glob_files(dir + '/f*', dir2 + '/f*')
        >>> len(files) == 2
        True
        >>> files[0] == f1
        True
        >>> files[1] == f3
        True
        >>> # globbing all matching files
        >>> files = glob_files(dir + '/f*', dir2 + '/f*', only_first=False)
        >>> len(files) == 3
        True
        >>> files[0] == f1
        True
        >>> files[1] == f2
        True
        >>> files[2] == f3
        True

    """
    out_files = []
    for f in files:
        gl = glob(f)
        if len(gl) > 0:
            if only_first:
                out_files.append(gl[0])
            else:
                for f in gl:
                    out_files.append(f)
        else:
            out_files.append(f)
    return out_files


def force_suffix_folder(dir_path, suffix):
    """
    Enforces path ``dir_path`` to be terminated with folder/file ``suffix``.

    Return:
        the resulting path (with ``suffix`` appended if not already present).

    Example:
        >>> dir_path = './my/path'
        >>> force_suffix_folder(dir_path, 'is_here')
        './my/path/is_here'
        >>> dir_path = './my/path/is_here'
        >>> force_suffix_folder(dir_path, 'is_here')
        './my/path/is_here'
    """
    if not re.match(r".*" + suffix + r"/?", dir_path):
        dir_path += os.sep + suffix
    return dir_path


def check_file(file_path, additional_msg=""):
    """
    Checks file ``file_path`` exists.

    Raises an exception if file doesn't exist.
    Otherwise returns the ``file_path`` passed as argument.

    Args:
        additional_msg: ``str``
            Message additionally printed if exception raised.

    .. seealso::
        :func:`.check_files`

    Example:
        >>> check_file('/etc/passwd')
        '/etc/passwd'
        >>> check_file('nonexistingfileforsureornot')
        Traceback (most recent call last):
        ...
        Exception: Error: the file nonexistingfileforsureornot doesn't exist.
    """
    if not exists(file_path):
        raise Exception("Error: the file " + file_path +
                        " doesn't exist." + additional_msg)
    return file_path


def check_files(*files):
    """
    Proceeds to a :func:`.check_file` for each file in ``files``.

    Return:
        ``None``

    .. seealso::
        :func:`.check_file`


    Example:
        >>> check_files('/etc/passwd', '/etc/hosts')
        >>> check_files('/etc/passwd', '/etc/hosts', 'likelynonexistingfile')
        Traceback (most recent call last):
        ...
        Exception: Error: the file likelynonexistingfile doesn't exist.

    """
    for f in files:
        check_file(f)


def count_file_lines(file):
    r"""
    Counts the number of lines in ``file``.

    Return:
        number of lines found.

    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> f1 = "f1-" + rand_suffix
        >>> f_out = open(f1, 'w')
        >>> f_out.writelines(["line 1\n", "line 2\n", "line 3\n"])
        >>> f_out.close()
        >>> count_file_lines(f1)
        3
        >>> remove_files(f1)

    """
    check_file(file)
    fd = open(file)
    n = len(fd.readlines())
    fd.close()
    return n


def truncate_file(file, nlines):
    r"""
    Truncates ``file`` to ``nlines`` number of lines.

    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> f1 = "f1-" + rand_suffix
        >>> f_out = open(f1, 'w')
        >>> f_out.writelines(["line 1\n", "line 2\n", "line 3\n"])
        >>> f_out.close()
        >>> count_file_lines(f1)
        3
        >>> truncate_file(f1, 1)
        >>> count_file_lines(f1)
        1
        >>> remove_files(f1)

    """
    check_file(file)
    fd = open(file)
    lines = fd.readlines()
    fd.close()
    fd = open(file, 'w')
    fd.writelines(lines[:nlines])
    fd.close()


def infer_path_rel_and_abs_cmds(argv):
    r"""
    This function is an helper to define which string (filename or filepath) to
    use to launch a program (``argv[0]``).

    This function can help to write a USAGE message for a script. Precisely, to
    determine how to print the program (as a filepath or just a name).

    The string is not the same if the current working directory is the parent
    directory of ``argv[0]`` (a relative path to the program might be used)
    or another directory (an absolute path to the program might be used).
    Besides, the program can also be available from a directory set in the PATH
    environment variable (in this case only the program filename is enough to
    launch it).

    Args:
        argv: ``list[str]``
            the arguments  of the program of interest (see ``sys.argv``).

    Return: ``tuple(str, str)``
        - ``tuple[0]``: the command to use in current working directory to run
          ``argv[0]``,
        - ``tuple[1]``: the command to use in another directory to run
          ``argv[0]``.
        ``tuple[0]`` can possibly be the same as ``tuple[1]``.

    Example:
        >>> # for a program in PATH
        >>> cwd_cmd, other_dir_cmd = infer_path_rel_and_abs_cmds(['ls'])
        >>> cwd_cmd == 'ls'
        True
        >>> other_dir_cmd == os.getcwd() + '/ls'
        True
        >>> # for a program in PATH but with absolute path given
        >>> cwd_cmd, odir_cmd = infer_path_rel_and_abs_cmds(['/usr/bin/ls'])
        >>> cwd_cmd == 'ls'
        True
        >>> odir_cmd == 'ls'
        True
        >>> # for a program not in PATH
        >>> script = 'nop232323.py'
        >>> exists(script)
        False
        >>> s = open(script, 'w')
        >>> s.writelines(['#!/usr/bin/env python3\n'])
        >>> s.write('from sys import argv\n')
        21
        >>> s.write('from py3toolset.fs import infer_path_rel_and_abs_cmds\n')
        51
        >>> s.writelines(["if __name__ == '__main__':\n"])
        >>> s.writelines(['    print(infer_path_rel_and_abs_cmds(argv))\n'])
        >>> s.close()
        >>> os.system("chmod +x "+script)
        0
        >>> import subprocess
        >>> ret = subprocess.run("./"+script, capture_output=True)
        >>> ret.stdout # doctest:+ELLIPSIS
        b"('./nop232323.py', '/.../nop232323.py')\n"
        >>> # 1st path is ./ because script is in cwd
        >>> # 2nd path is absolute path to use the script from any directory
        >>> remove_files(script)
    """
    prog_name = basename(argv[0])
    if dirname(argv[0]) in environ['PATH'].split(pathsep):
        # the script is in path we don't need to print location in usage
        prog_abs_path = ""
        prog_rel_path = ""
    elif argv[0].startswith(os.path.sep):
        # absolute path
        prog_abs_path = dirname(argv[0])
        prog_rel_path = dirname(argv[0])
    else:
        # relative path
        prog_abs_path = join(getcwd(), dirname(argv[0]))
        prog_abs_path = prog_abs_path.replace(os.path.sep+'.', '')
        prog_rel_path = dirname(argv[0])
    cwd_cmd = join(prog_rel_path, prog_name)
    other_dir_cmd = join(prog_abs_path, prog_name)
    return cwd_cmd, other_dir_cmd


def copy_file_with_rpath(path, targetdir):
    """
    Copies file ``path`` into ``targetdir`` keeping its relative path.

    For example, ``path = 'dir1/dir2/dir3/file'`` is copied as
    ``targetdir + '/dir1/dir2/dir3/file'

    ``targetdir`` and intermediate folders are created recursively if needed.

    Args:
        path: ``str``
            relative path of the file.
        targetdir: ``str``
            target directory to copy the file into (keeping its relative path).

    Example:
        >>> from random import randint
        >>> rand_suffix = str(randint(1, 2**10))
        >>> # create a folder and dummy files
        >>> parent_dir = "my_dir" + rand_suffix
        >>> os.mkdir(parent_dir)
        >>> f1 = os.path.join(parent_dir, "f1")
        >>> f_out = open(f1, 'w')
        >>> f_out.writelines(["Test test test"])
        >>> f_out.close()
        >>> f2 = os.path.join(parent_dir, "f2")
        >>> f2_out = open(f2, 'w')
        >>> f2_out.writelines(["Test2 test2 test2"])
        >>> f2_out.close()
        >>> target_dir = 'new_dir' + rand_suffix
        >>> copy_file_with_rpath(f2, target_dir)
        >>> exists(os.path.join(target_dir, f2))
        True
        >>> print(os.path.join(target_dir, f2)) # doctest:+ELLIPSIS
        new_dir.../my_dir.../f2
        >>> remove_dirs(target_dir, parent_dir)

    """
    if path.startswith(sep):
        raise ValueError('path must be relative')
    dpath = join(targetdir, dirname(path))
    folders = dpath.split(sep)
    bpath = ""
    for f in folders:
        bpath += f
        bpath += sep
        if not exists(bpath):
            mkdir(bpath)
    copyfile(path, join(targetdir, path))
