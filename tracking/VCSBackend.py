#
# VCSBackend.py
#

"""
package oompa.tracking

generic base for Version Control System backend
(parent to git, hg, svn, ...)

"""

import os

# XXX need lib across all projects to hide python2 vs python3 diffs in urlparse
try:
    # python3
    from urllib.parse import urlparse
except ImportError:
    from urlparse     import urlparse
    pass


class VCSBackend:
    """
    
    base class for version control backend.
    (will have subclasses for hg, bzf, svn, git, ...)

    """

    _type   = None

    verbose = False


    def __init__(self, logger = None):

        # some backends require changing current directory, so we use this for push/pop
        self._folder_stack = []

        self.logger        = logger

        return


    def log(self, message = None):

        if message is None:
            message = ""
            pass

        if self.logger is not None:
            self.logger.info(message)
            pass
        
        return
        

    

    def _determine_project_name(self, source_spec):
        """

        figure out project name from a url, or url and requested project name

          http://git.code.sf.net/p/guitarix/git guitarix  -> guitarix

        this default implementation uses tail of the source url

        """

        pieces = source_spec.split()

        if len(pieces) == 2:
            return pieces[1]

        result = urlparse(source_spec)

        # XXX hack - need a plugin set of rules

        if result.netloc == "git.code.sf.net":
            # pick "guitarix" from /p/guitarix/git
            project_name = os.path.basename(os.path.dirname(result.path))
        else:
            tail                 = os.path.basename(result.path)
            project_name, suffix = os.path.splitext(tail)
            pass

        return project_name



    def _create_vcs_folder(self, project_name, base_folder = None):

        if base_folder is None:
            base_folder = os.getcwd()
            pass

        project_path = os.path.join(base_folder,  project_name)
        vcs_path     = os.path.join(project_path, self._type)

        print("  vcs_path: %s" % vcs_path)

        # XXX use file_utils
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            pass

        if not os.path.exists(vcs_path):
            os.makedirs(vcs_path)
            pass

        return vcs_path


    def push_folder(self, folder):
        
        # print("push_folder: %s" % folder)

        self._folder_stack.append(os.getcwd())

        # print("   folder_stack: %s" % self._folder_stack)

        if self.verbose:
            print("  cd %s" % folder)
            pass

        os.chdir(folder)

        return

    def pop_folder(self):

        folder = self._folder_stack.pop()
        
        # print("pop_folder: %s" % folder)

        os.chdir(folder)

        return folder

    def checkout(self, source_spec, *args):
        """
        returns local folder where project was checked out
        """

        raise NotImplementedError

    def update(self, project):
        """

        perform whatever steps are necessary to update the project,
        synching it with a remote repository

        """

        raise NotImplementedError

    pass

