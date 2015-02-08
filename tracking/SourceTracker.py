#
# SourceTracker.py
#

"""
packge oompa.tracking

"""

import datetime
import os
import sys          # for stdout

from pylib.util             import file_utils

from oompa.tracking.Project import Project
from oompa.tracking         import vcs_utils
from oompa.tracking         import VCSBackendFactory

from oompa.tracking.Project import NotAProjectException


class SourceTracker:
    """

    support for tracking/updating an entire tree of tracked projects,
    under a variety of source code control systems
    
    """

    def __init__(self, config = None, out_stream = None):
        """
        require a config
        """

        self.config     = config

        tracking_folder = config is not None and config.get('tracking.folder')

        if not tracking_folder:
            # XXX probably does not work on windows
            home            = os.environ["HOME"]
            tracking_folder = os.path.join(home, "src", "tracking")
            pass
        
        self.tracking_folder = tracking_folder
        
        # TODO: maybe should use real logging?

        if out_stream is None:
            out_stream = sys.stdout
            pass

        self.out_stream = out_stream

        return

    def setOutStream(self, out_stream):

        self.out_stream = out_stream

        return

    def print(self, message = None):

        if message is None:
            message = ""
            pass

        self.out_stream.write("%s\n" % message)
        
        return


    def get_path_in_tracker_tree(self, project):
        """
        """

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

        project         = Project(project_path, tracker = self)
        vcs_root        = project.get_vcs_folder()

        self.print("Sourcetracker.track(): %s - %s" % ( project.path, vcs_root ))

        if vcs_root is None:
            self.print("  XXX could not identify a vcs subfolder for for project: %s" %
                       project.path)
            return None


        #
        # figure out where we will put the project, within the tracking
        # tree
        #
        path_in_tracker = self.get_path_in_tracker_tree(project.path)

        self.print("   path_in_tracker: %s" % path_in_tracker)
        
        if os.path.exists(path_in_tracker):

            if not replace:
                self.print("  not replacing existing path in tracker: %s" % path_in_tracker)
                return

            os.remove(path_in_tracker)
            pass

        file_utils.create_folder_for(path_in_tracker)
        
        self.print("ln -s %s %s" % ( path_in_tracker, vcs_root ))

        os.symlink(vcs_root, path_in_tracker)
        
        return path_in_tracker


    def untrack(self, project_path):
        """

        TODO: option to delete the src, too

        """

        project         = Project(project_path)
        vcs_root        = project.get_vcs_folder()

        # self.print("Sourcetracker.untrack(): %s - %s" % ( project.path, vcs_root ))

        #
        # figure out where we will put the project, within the tracking
        # tree
        #
        path_in_tracker = self.get_path_in_tracker_tree(project.path)

        self.print("   removing path_in_tracker: %s" % path_in_tracker)

        if os.path.exists(path_in_tracker):
            os.remove(path_in_tracker)
        else:
            self.print("  not tracking project")
            pass

        return


    def checkout(self, source_spec, *rest):
        """
        
        check out the project specified by source_spec (usually a url (git, hg, svn, ...))
        
        """

        vcs_type = vcs_utils.detect_vcs_type_from_source(source_spec)

        if vcs_type is None:
            self.print("SourceTracker.checkout(): unknown vcs type: %s" % source_spec)
            xxx
            pass
        
        backend  = VCSBackendFactory.get_backend(project_type = vcs_type,
                                                 out_stream   = self.out_stream)
        result   = backend.checkout(source_spec, *rest)

        return result


    def update_project(self, project_path):
        """

        """
        
        project  = Project(project_path, self)
        result   = project.update()

        if result is not None and result != 0:
            self.out_stream.write("  result: %s - %s\n" % ( project_path, result, ))
            # XXX only if something happened
            self.print()
            pass

        self.out_stream.flush()

        return

    
    def update_folder(self, folder):
        """
        update a folder and any projects below it
        """

        vcs_type = vcs_utils.determine_vcs_type(project_path = folder)

        # self.print("SourceTracker.update_folder(): %s (vcs_type: %s)" % ( folder, vcs_type ))

        if vcs_type:
            return self.update_project(folder)

        children = os.listdir(folder)

        for child in children:
            path = os.path.join(folder, child)
            if os.path.isdir(path):
                result = self.update_folder(path)
                pass
            pass

        return
        

    def update_all(self):
        """
        update all projects under the root tracking folder

        """
        return self.update_folder(self.tracking_folder)
        

    def update(self, *projects):
        """

        update some or all projects that have been previously tracked

        projects, if supplied, is a list of paths.
        may or may not be under tracking tree
        """
        
        self.print()
        self.print("# %s - start tacker update" % datetime.datetime.today().strftime("%Y%m%d-%H:%M"))
        self.print()

        if not projects:
            return self.update_all()

        for project in projects:
            result = self.update_folder(project)
            pass

        return


    def dumpSourceURLsInFolder(self, folder):
        


        # print("dumpSourceURLsInFolder(): %s" % folder)

        try:
            project  = Project(folder, self)

            print("%s\t%s\t%s" % ( project.get_vcs_folder(), project.vcs_type, project.getSourceURL() ))

        except NotAProjectException:
            #
            # not a project.  dive in to children to find projects
            #
            children = os.listdir(folder)
            
            for child in children:
                path = os.path.join(folder, child)
                if os.path.isdir(path):
                    self.dumpSourceURLsInFolder(path)
                    pass
                pass
            pass

        return

    def dumpSourceURLs(self, *projects):
        """
        
        dump all the source urls in a format that can be used to 
        set up tracking on another system
        
        output includes location in source tree 

        """
        
        if projects:
            for project in projects:
                self.dumpSourceURLsInFolder(project)
                pass
            return

        self.dumpSourceURLsInFolder(self.tracking_folder)

        return


    def importDumpedURLs(self, *paths):
        """

        """

        # XXX
        local_base = "/Users/jeff/src"
        
        for path in paths:

            print("importDumpedURLs: %s" % ( path, ))

            for line in open(path):
                line = line.strip()
                if not line or line[0] == "#":
                    continue

                local_path, type, url = line.split("\t")

                # need to remove prefix from other machine
                # (e.g., /home/jeff/src).  expects that /src/ is in path somewhere.
                #
                # remove "tracking/" - should not have included in export
                #
                # need to remove the tail (because in tracking tree, it's usually
                # repeated - "src/scala/akka/akka"

                src_index  = local_path.find("/src/")

                if src_index == -1:
                    xxx
                
                local_path    = local_path[src_index+5:]
                local_path    = local_path.replace("tracking/",   "")
                local_path    = os.path.dirname(local_path)

                parent_folder = os.path.dirname(local_path)
                
                print("  %s %s %s" % ( parent_folder, type, url ))
                # print("  local_path: %s" % local_path)
                
                if os.path.exists(local_path):
                    print("  already exists: %s" % local_path)
                    continue

                full_parent_folder = os.path.join(local_base, parent_folder)

                if not os.path.exists(full_parent_folder):
                    os.makedirs(full_parent_folder)
                    pass
                
                # XXX code expects that we are checking out in to "os.cwd"
                os.chdir(full_parent_folder)
                
                project_folder = self.checkout(url)

                if project_folder is None:
                    xxx
                    pass
    
                link_path      = self.track(project_folder)
                pass
            pass
        
        return
    
    pass
    
