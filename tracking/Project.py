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

        self._vcs_folder = vcs_utils.find_vcs_folder(project = self)

        self._backend    = None

        # if out_stream is None:
        #    out_stream = tracker.out_stream
        #    pass
        #
        # self.out_stream  = out_stream
        # 
        # # XXX ???
        # # XXX bridging to new logging system
        # self._out_stream = self._tracker.out_stream
        
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


    def update(self):
        """
        use project's VCS backend to update source from remote
        """
        return self._get_backend().update(self)

    def getSourceURL(self):

        return self._get_backend().getSourceURL(self)

    
    def getTagInfo(self):

        return self._tracker.getTagInfo(self)

    def log(self, message = None):
        self._tracker.log(message)
        return
        
    
    pass
