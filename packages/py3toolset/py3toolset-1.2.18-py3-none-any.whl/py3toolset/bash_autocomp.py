"""
Module for installing bash autocompletion scripts.
"""

import os
from os.path import exists
import sys

from py3toolset.cmd_interact import ask_yes_or_no
from py3toolset.fs import get_prog_parent_dir
from py3toolset.txt_color import warn, col, Color


def propose_bashautocomp(autocomp_script):
    """
    Prompts user for a Bash completion script install for the current running
    program (``sys.argv[0]``).

    User decides not to/to install Bash completion script in his home
    directory.
    User is asked whether to prompt her/him again the next time.

    The script install is done as advised in `bash-completion doc
    <https://github.com/scop/bash-completion/blob/master/README.md>`_.
    """
    prog_path = get_prog_parent_dir()
    # TODO: take care that the script dir might not be writable
    autocomp_script_src = prog_path + os.sep + autocomp_script
    dontask_again_file = prog_path + os.sep + ".dontask_autocomp_install"
    src_command = "source " + autocomp_script_src + " 2>/dev/null\n"
    # stderr ignored in case of a later script deletion
    # otherwise user will be bothered with the error every time
    # (s)he launches a Bash
    if (not exists(dontask_again_file) and
        (not exists(INSTALL_PATH) or
         not _is_cmd_in_install_conf(src_command))):
        warn("Bash command completion feature for " + sys.argv[0] +
             " isn't installed on your system.")
        print("Do you want to install it in ", INSTALL_PATH+"? ")
        answer = ask_yes_or_no()
        if answer[0] == "y":
            f = open(INSTALL_PATH, "a")
            f.write(src_command)
            f.close()
            print(col(Color.GREEN, "Bash completion feature installed! But"
                      " you need to start a new bash session to have"
                      " it applied."))
        else:
            print("Ask again the next time ?")
            answer = ask_yes_or_no()
            if answer[0] == "n":
                print(dontask_again_file)
                f = open(dontask_again_file, "w")
                f.write("This file is a marker for avoiding the program "
                        + sys.argv[0] +
                        " to ask again if you want bash completion"
                        " to be enabled. Delete it to be asked again!\n")
                f.close()


def _is_cmd_in_install_conf(src_command):
    """
    Test if a bash completion facility corresponding to src_command is already
    installed in bash_completion file.
    """
    with open(INSTALL_PATH) as f:
        return [line for line in f.readlines()].count(src_command) > 0


INSTALL_PATH = os.getenv("HOME")+os.sep+".bash_completion"
