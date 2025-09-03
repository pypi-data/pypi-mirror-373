"""
This module manages the backup and restoration of a list of files.
"""

import os
from os.path import dirname, isdir, basename, exists
import re
from shutil import copyfile

from py3toolset.cmd_interact import ask_yes_or_no
from py3toolset.txt_color import print_frame

# default backup folder
BACKUP_FOLDER = ".backup"


def work_on_copies(*files, answer="", backup_folder=BACKUP_FOLDER,
                   header_msg=None, hdr_frame=True):
    """
        Saves/Restores original ``files`` in ``backup_folder``.

        The first call makes a copy, the next one a restoration.
        All ``files`` must be in the same parent directory.
        The function quits the program if user refused to restore files.

        Args:
            answer: ``str``
                if "yes" then the function auto-restores files from backup
                (without prompting user for it).
                Defaultly, the question is asked to user.
            backup_folder: ``str``
                The folder into which the files are backed up.
                It is located in the same parent directory as ``files``.
            header_msg: ``str``
                The header message to print before saving/restoring ``files``.
                Defaultly (``None``) no message.

        Example:
            >>> from random import randint
            >>> rand_suffix = str(randint(1, 2**10))
            >>> # create a folder and dummy files
            >>> parent_dir = "test_work_on_copies" + rand_suffix
            >>> os.mkdir(parent_dir)
            >>> f1 = os.path.join(parent_dir, "f1")
            >>> f_out = open(f1, 'w')
            >>> f_out.writelines(["Test test test"])
            >>> f_out.close()
            >>> f2 = os.path.join(parent_dir, "f2")
            >>> f2_out = open(f2, 'w')
            >>> f2_out.writelines(["Test2 test2 test2"])
            >>> f2_out.close()
            >>> # now try work_on_copies
            >>> work_on_copies(f1, f2, answer="y")
            Saving original files to .backup
            >>> # do some modifications
            >>> f_out = open(f1, 'w')
            >>> f_out.writelines(["Not the same test"])
            >>> f_out.close()
            >>> # file f1 is modified
            >>> f_out = open(f1, 'r')
            >>> print(f_out.readlines()[0])
            Not the same test
            >>> # restore f1
            >>> work_on_copies(f1, f2, answer="y") #doctest:+ELLIPSIS
            Getting back original files from .backup
            list of files to be restored: test_work_on_copies...
            The previous file working copy will be overridden...
            Do you want to proceed?
            Copying test_work_on_copies...
            Copying test_work_on_copies...
            >>> f_out = open(f1, 'r')
            >>> print(f_out.readlines()[0])
            Test test test
            >>> f_out.close()
            >>> # file f1 has been restored

    """
    if header_msg:
        if hdr_frame:
            print_frame(header_msg)
        else:
            print(header_msg)
    pdir = dirname(files[0])
    if re.match(pdir, r"\s") is not None:
        pdir = "."
    sav_dir_path = pdir + os.sep + backup_folder
    # print("backup sac copy dir.: "+sav_dir_path)
    if isdir(sav_dir_path):
        print("Getting back original files from " + backup_folder)
        print("list of files to be restored: "+", ".join(files))
        print("The previous file working copy will be overridden"
              " (if a corresponding backup file exists)!\n"
              "Do you want to proceed?")
        answer = ask_yes_or_no(answer)
        if answer[0] == 'n':
            print("Quitting, nothing done.")
            exit()
        for _file in files:
            saved_sac = sav_dir_path + os.sep + basename(_file)
            if exists(saved_sac):
                print("Copying " + saved_sac + " to " + _file)
                copyfile(saved_sac, _file)
            else:
                print("Backup doesn't exist in " +
                      sav_dir_path + "." +
                      " Keeping file: " + _file)
                print("Saving the file above in " + sav_dir_path)
                copyfile(_file, saved_sac)
    else:
        print("Saving original files to " + backup_folder)
        os.mkdir(sav_dir_path)
        for _file in files:
            copyfile(_file, sav_dir_path + os.sep + basename(_file))
