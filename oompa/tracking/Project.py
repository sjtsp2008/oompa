#
# Project.py
#

import os

# XXX should be using pyvcs
from oompa.tracking import VCSBackendFactory
from oompa.tracking import vcs_utils

class NotAProjectException(Exception):
    pass


class Project:
    """

    """

    def __init__(self, 
                 path, 
                 tracker    = None,
                 out_stream = None):

        # note that path is the "tracking" path
        self.path      = os.path.abspath(path)
        self._tracker  = tracker

        self.vcs_type  = vcs_utils.determine_vcs_type(project = self)

        if self.vcs_type is None:
            raise NotAProjectException(path)

        # the root folder containing .git/, .hg/, whatever
        self._vcs_folder = vcs_utils.find_vcs_folder(project = self)

        # class that can execute "protocol" for git, hg, bzr, ...
        self._backend    = None

        # we don't need this ourselves - just pass through to backend
        # self._verbose = False
        
        return

    
    def basename(self):

        return os.path.basename(self.path)

    def get_tracking_path(self):

        return self.path

    def get_src_path(self):

        # assumes we are starting from tracking path.  i'm not sure that's always true
        path = self.path

        if "/tracking/" not in path:
            return path
        
        # the tracking path has the leaf folder twice at the end

        # XXX why is this complicated?
        # path = os.readlink(path)
        tail     = os.path.basename(path) 
        vcs_path = os.readlink(os.path.dirname(path))
        path     = os.path.join(vcs_path, tail)
        
        return path

    def get_vcs_folder(self):

        return self._vcs_folder


    def _get_backend(self):
        """
        return the VCS backend engine for this project
        """
        
        if self._backend is not None:
            return self._backend

        self._backend = VCSBackendFactory.get_backend(self.vcs_type)

        return self._backend


    def setVerbose(self, verbose):

        # note that we ourselves don't care about the flag
        
        self._get_backend().verbose = verbose
        

    def update(self):
        """
        use project's VCS backend to update source from remote
        """
        return self._get_backend().update(self)

    
    def reset(self):
        """
        use project's VCS backend to perform a reset.  mostly for git strangeness, i think
        """
        return self._get_backend().reset(self)

    
    def getSourceURL(self):

        return self._get_backend().getSourceURL(self)

    
    def getTagInfo(self):

        return self._tracker.getTagInfo(self)

    def log(self, message = None):
        self._tracker.log(message)
        return
        
    
    pass
