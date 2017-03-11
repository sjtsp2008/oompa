#
# track_utils.py
#

"""
packge oompa.tracking

TODO:
    - most of this must be wrapped in a 
"""

import os

from oompa.tracking import file_utils


class Tracker:
    """
    overall coordinator
    """
    
    def __init__(self, config = None):
        """
        TODO: *require* a config
        """

        self.config     = config

        tracking_folder = config is not None and config.get('tracking.folder')

        if not tracking_folder:
            # XXX probably does not work on windows
            home            = os.environ["HOME"]
            tracking_folder = os.path.join(home, "src", "tracking")
            pass
        
        self.tracking_folder = tracking_folder

        #
        # XXX discover from plugins, or get from config
        # 
        self._vcs_types  = [ 'hg', 'bzr', 'svn', 'git', 'cvs' ]

        return

        
    def determine_vcs_type(self, project):
        """

        project is a path

        TODO:
          - memoize into a registry
        """
        

        return vcs_type



    def find_vcs_folder(self, path):
        """
        
          in general, assumes a convention: path/{svn,hg,bzr,...}/<checkout>

        note that if multiple types of checkout exist, we will pick
        the first

        TODO:
            - delegate to determine_vcs_type
        """
        
        for vcs_type in self._vcs_types:

            vcs_folder = os.path.join(path, vcs_type)

            if os.path.exists(vcs_folder):
                return vcs_folder
            pass

        #
        # have to be more clever
        #

        return None



    def get_path_in_tracker_tree(self, project):
        """
        """

        # print "get_path_in_tracker_tree(): %s" % project

        #
        # get the tail below "src"
        #
        pieces  = project.split(os.sep)
        
        index   = pieces.index("src")

        if index == -1:
            # XXX handle other schemes
            xxx
            pass

        tail    = pieces[index+1:]
        path    = os.path.join(self.tracking_folder, *tail)
        
        return path


    def track(self, project_path, replace = False):
        """

        establish tracking for the project.
        assumes that project_path has some sort of checkout child
        folder

        """

        project_path = os.path.abspath(project_path)

        #
        # figure out what type of checkout it it
        #
        vcs_root        = self.find_vcs_folder(project_path)
        
        #
        # figure out where we will put the project, within the tracking
        # tree
        #
        path_in_tracker = self.get_path_in_tracker_tree(project_path)
        
        if os.path.exists(path_in_tracker):

            if not replace:
                return

            os.remove(path_in_tracker)
            pass
        
        file_utils.create_folder_for(path_in_tracker)
        
        # print "ln -s %s %s" % ( path_in_tracker, vcs_root )

        os.symlink(vcs_root, path_in_tracker)
        
        return path_in_tracker

    pass
    
