#
# SourceTracker.py
#

"""
packge oompa.tracking

"""

import datetime
import logging
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

    logger = logging.getLogger(__name__)

    
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
        
        return


    def log(self, message = None):
        """
        log the message at info level
        """
        
        if message is None:
            # we need one line
            message = "\n"
            pass

        for line in message.splitlines():
            self.logger.info("%s" % line)
            pass
        
        return


    def getPathInTrackerTree(self, projectPath):
        """

        return the tracking symlink 
        
        XXX there can now be many links for a given project

        """

        #
        # get the tail below "src"
        #
        pieces  = projectPath.split(os.sep)
        index   = pieces.index("src")

        if index == -1:
            # XXX handle other schemes
            xxx
            pass

        tail = pieces[index+1:]
        
        return os.path.join(self.tracking_folder, *tail)


    def findTrackingLinks(self, projectPath, root = None):
        """
        return all links under root that point to specified project

        recursive

        if root not specified, start at self.tracking_folder
        """
        
        if root is None:
            root = self.tracking_folder
            pass
        
        # print("findTrackingLinks(): %s  %s" % ( projectPath, root ))

        # i tried using os.walk, and something did not work quite right
        
        for child in os.listdir(root):

            # XXX cheating
            if child == "git":
                continue
            
            childPath = os.path.join(root, child)

            # print("    child: %s" % childPath)

            if os.path.islink(childPath):

                realPath = os.path.realpath(childPath)
                # print("     link -> %s" % realPath)

                if realPath.startswith(projectPath):
                    # print("       WINNER")
                    yield childPath
                    pass
                pass
            elif os.path.isdir(childPath):
                for link in self.findTrackingLinks(projectPath, childPath):
                    yield link
                    pass
                pass
            pass

        return
    

    def track(self, project_path, replace = False):
        """establish tracking for the project.

        assumes that project_path has some sort of checkout child
        folder

        """

        project         = Project(project_path, tracker = self)
        vcs_root        = project.get_vcs_folder()

        self.log("Sourcetracker.track(): %s - %s" % ( project.path, vcs_root ))

        if vcs_root is None:
            self.log("  XXX could not identify a vcs subfolder for for project: %s" %
                     project.path)
            return None

        #
        # figure out where we will put the project, within the tracking
        # tree
        #
        path_in_tracker = self.getPathInTrackerTree(project.path)

        # self.log("   path_in_tracker: %s" % path_in_tracker)
        
        if os.path.exists(path_in_tracker):

            if not replace:
                self.log("  not replacing existing path in tracker: %s" % path_in_tracker)
                return

            os.remove(path_in_tracker)
            pass

        file_utils.create_folder_for(path_in_tracker)
        
        self.log("  ln -s %s %s" % ( path_in_tracker, vcs_root ))

        os.symlink(vcs_root, path_in_tracker)
        
        return path_in_tracker


    def untrack(self, project_path):
        """
        stop tracking a project

        does not delete the source project, just the tracking links

        TODO: option to delete the src, too
        TODO: use code from self.moveFolder to untrack *all* symlinks to project

        """

        project   = Project(project_path)
        vcs_root  = project.get_vcs_folder()

        # self.log("Sourcetracker.untrack(): %s - %s" % ( project.path, vcs_root ))

        #
        # figure out where we will put the project, within the tracking
        # tree
        #
        path_in_tracker = self.getPathInTrackerTree(project.path)

        self.log("   removing path_in_tracker: %s" % path_in_tracker)

        if os.path.exists(path_in_tracker):
            os.remove(path_in_tracker)
        else:
            self.log("  not tracking project")
            pass

        return


    
    def checkout(self, source_spec, *rest):
        """
        
        check out the project specified by source_spec (usually a url (git, hg, svn, ...))
        
        """

        self.log("SourceTracker.checkout(): %s %s" % ( source_spec, rest ))
        
        vcs_type = vcs_utils.detect_vcs_type_from_source(source_spec)

        if vcs_type is None:
            self.log("SourceTracker.checkout(): unknown vcs type: %s" % source_spec)
            return None

        backend  = VCSBackendFactory.get_backend(project_type = vcs_type)
        result   = backend.checkout(source_spec, *rest)

        self.log()
        
        return result


    def moveFolders(self, *args):
        """
        move specified project folders and update tracking symlinks

          src ... dest

        """
        
        # assumes we are in "real" source folder, versus tracking folder

        if len(args) < 2:
            xxx
            pass
        
        # TODO: support fully recursive glob

        destFolder    = args[-1]
        sourceFolders = args[:-1]

        absDestFolder = os.path.abspath(destFolder)
        
        # print("  dest: %s" % absDestFolder)

        assert os.path.exists(destFolder)

        for sourceFolder in sourceFolders:

            # TODO: is it a folder or a glob?

            sourceFolder    = os.path.abspath(sourceFolder)
            tail            = os.path.basename(sourceFolder)
            newSourceFolder = os.path.join(absDestFolder, tail)

            trackingLinks   = self.findTrackingLinks(sourceFolder)
            trackingLinks   = list(trackingLinks)

            if len(trackingLinks) > 1:
                # which of them is "the original" (that should be deleted and moved), versus the one that needs to be replaced?
                xxx
                pass
            
            # identify *all* links the project in tracking tree)
            #   (there may be multiple)

            # move the project

            print("  move %s -> %s" % ( sourceFolder, newSourceFolder ))
            os.rename(sourceFolder, newSourceFolder)
            
            # replace the links
            # may have to
            #    just delete the link, and then do a new track

            for trackingLink in trackingLinks:

                print("    rm %s" % trackingLink)
                os.remove(trackingLink)

                print("    track: %s" % newSourceFolder)
                self.track(newSourceFolder)
                
                # if original tracking parent is now empty, delete it (and on up ...)

                linkParentFolder = os.path.dirname(trackingLink)

                print("    try deleting the parent of the link: %s" % linkParentFolder)
                
                pass
            
            pass
        
        return
    

    def update_project(self, project_path):
        """

        """
        
        project  = Project(project_path, self)
        result   = project.update()

        if result is not None and result != 0:
            self.log("  result: %s - %s\n" % ( project_path, result, ))
            # XXX only if something happened
            self.log()
            pass

        # self.out_stream.flush()

        return

    
    def update_folder(self, folder):
        """
        update a folder and any projects below it
        """

        vcs_type = vcs_utils.determine_vcs_type(project_path = folder)

        # self.log("SourceTracker.update_folder(): %s (vcs_type: %s)" % ( folder, vcs_type ))

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
        
        self.log()
        self.log("# %s - start tacker update" % datetime.datetime.today().strftime("%Y%m%d-%H:%M"))
        self.log()

        if not projects:
            self.update_all()
        else:
            for project in projects:
                result = self.update_folder(project)
                pass
            pass
        
        self.log()
        self.log("# %s - finished tacker update" % datetime.datetime.today().strftime("%Y%m%d-%H:%M"))
        self.log()

        return



    def getProjects(self, folder):
        """
        generate stream of all Projects at and below folder
        """

        try:
            yield Project(folder, self)
        except NotAProjectException:
            #
            # folder was not a project.  dive in to children to find projects
            #
            children = os.listdir(folder)
            
            for child in children:
                childFolder = os.path.join(folder, child)
                if os.path.isdir(childFolder):
                    for project in self.getProjects(childFolder):
                        yield project
                        pass
                    pass
                pass
            pass

        return
        

    
    def dumpSourceURLsInFolder(self, folder):

        # print("dumpSourceURLsInFolder(): %s" % folder)

        for project in self.getProjects(folder):
            print("%s\t%s\t%s" % ( project.get_vcs_folder(), project.vcs_type, project.getSourceURL() ))            
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

                # XXX temp
                if type == "svn":
                    print("we don't check out %s projects yet - %s %s" % ( type, local_path, url ))
                    continue
                
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
                
                local_path      = local_path[src_index+5:]
                local_path      = local_path.replace("tracking/",   "")
                local_path      = os.path.dirname(local_path)

                full_local_path = os.path.join(local_base, local_path)

                # print("full_local_path: %s" % full_local_path)

                if os.path.exists(full_local_path):
                    # if verbose:
                    # print("  already exists: %s" % full_local_path)
                    continue
                
                parent_folder      = os.path.dirname(local_path)
                full_parent_folder = os.path.join(local_base, parent_folder)
                
                print("  %s %s %s" % ( full_parent_folder, type, url ))

                if not os.path.exists(full_parent_folder):
                    os.makedirs(full_parent_folder)
                    pass
                
                # XXX code expects that we are checking out in to "os.cwd"
                os.chdir(full_parent_folder)
                
                project_folder = self.checkout(url)

                if project_folder is None:
                    print("  could not check out: %s" % url)
                    continue
    
                link_path      = self.track(project_folder)
                pass
            pass
        
        return


    def findProjects(self, *patterns):
        """
        simple grep over source tree folders/files
        """
        
        # TODO: create a regex over all args
        
        for project in self.getProjects(self.tracking_folder):

            matched = False

            for pattern in patterns:
                if project.path.find(pattern) != -1:
                    matched = True
                    break
                pass

            if matched:
                print("%s" % project.path)
                pass
            pass
        
        return
                     
    pass
    
