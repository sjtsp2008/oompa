#
# file_utils.py
#

"""
misc tools for working with files and file systems
"""

import os
import shutil
import stat

# import do_command

_trace_backup = 0


def get_next_backup_filename(path):
    """
    returns the full path

    XXX don't need to separate the base_pat, i think
        pass in optional list of suffixes (interpolatable)
    """

    if not os.path.exists(path):
        return None

    base_path, filename = os.path.split(path)
    
    #
    # XXX probably sub-optimal
    #

    next_filename = filename + "~"

    backup_path = os.path.join(base_path, next_filename)
    
    if not os.path.exists(backup_path):

        return backup_path

    else:

        #
        # XXX this approach is vulnerable to "holes".  is emacs?
        #     (it wouldn't be hard to get the max, via a glob)
        #
        
        index = 1

        while 1:

            if _trace_backup > 2:
                print("  filename: " + filename)
            
            backup_path = os.path.join(base_path,
                                       filename + ( ".~%d~" % index))

            if not os.path.exists(backup_path):
                return backup_path

            index = index + 1
            

        


def backup(path):
    """
    copy the file name by path to ~, then .~1~, ...
    """
    
    if _trace_backup > 0:
        print("backup: " + path)
    
    backup_filename = get_next_backup_filename(path)

    if _trace_backup > 1:
        print("backup_filename: " + str(backup_filename))

    if backup_filename:

        if _trace_backup > 1:
            print("  copying %s to %s: " % ( path, backup_filename ))
            pass
        
        result = shutil.copyfile(path, backup_filename)
        pass

    return


def get_file_size(path):

    try:
        stat_tuple = os.stat(path)

        return stat_tuple[stat.ST_SIZE]
    
    # except OSError, details:
    except OSError as details:
        return 0
    
    return

def get_mod_time(filename):
    """
    returns a DateTime

    throws ??? (IOError?)
    """

    from DateTime import localtime

    tuple = os.stat(filename)

    return (localtime(tuple[8]))

    
# XXX - catch up to latest official

def create_folder_for(path, mode = None):

    parent = os.path.dirname(path)

    if os.path.exists(parent):
        # TODO: check that perms match
        return

    # print("create_folder_for: %s (parent: %s)" % ( path, parent ))

    if mode is not None:
        return os.makedirs(parent, mode)

    return os.makedirs(parent)
