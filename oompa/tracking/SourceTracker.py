#
# SourceTracker.py
#

"""
packge oompa.tracking

"""

import datetime
import logging
import os
import random
import re
import shutil
import sys          # for stdout

from oompa.tracking             import file_utils

from oompa.tracking.Project     import Project
from oompa.tracking             import vcs_utils
from oompa.tracking             import VCSBackendFactory

from oompa.tracking.Project     import NotAProjectException
from oompa.tracking.TagManager  import TagManager


class SourceTracker:
    """

    support for tracking/updating an entire tree of tracked projects,
    under a variety of source code control systems
    
    """

    logger = logging.getLogger(__name__)

    
    def __init__(self, config = None, out_stream = None):
        """
        TODO: just require a config - doesn't work without
        """

        self.config     = config

        tracking_folder = config is not None and config.get('tracking.folder')

        if not tracking_folder:
            # XXX probably does not work on windows
            home            = os.environ["HOME"]
            tracking_folder = os.path.join(home, "src", "tracking")
            pass
        
        self.tracking_folder = tracking_folder

        self._tag_mgr        = TagManager(config,
                                          tags_filename = "project-tags.tsv")

        # XXX this is kind of a wart - sampling
        self._sampleProb = None
        self._sampleProb = 0.20
        
        return


    def setSampleProb(self, sampleProb):

        if sampleProb is None:
            # TODO: does this mean "keep the default", or "really set it to None again"?
            return
        
        if isinstance(sampleProb, str):
            sampleProb = int(sampleProb)
        
        if isinstance(sampleProb, int):
            sampleProb = sampleProb / 100.0

        self._sampleProb = sampleProb

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


    def untrack(self, project_path, keep_src = False):
        """
        stop tracking a project, by removing tracking links

        if keep_src is False, deletes the source.  if True, keeps it.

        assumes that the project_path is in the source tree

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

        if not keep_src:
            self.log("  removing source: %s" % project_path)
            shutil.rmtree(project_path)
            pass
        
        return



    def _getTagsFromProjectFolder(self, tags, project_folder):

        tags        = []
        
        parts       = project_folder.split(os.sep)
        # strip off project name istelf
        parts       = parts[:-1]
        
        while parts[-1] != "src":
            tags.append(parts[-1])
            parts = parts[:-1]
            pass

        # general-to-specifc seems more satisfying
        tags.reverse()
        
        return tags
    
    
    def checkout(self, source_spec, *rest):
        """check out the project specified by source_spec (usually a url
        (git, hg, svn, ...))

        """

        self.log("SourceTracker.checkout(): %s %s" % ( source_spec, rest ))

        source_spec = vcs_utils.normalize_source_spec(source_spec)
        
        vcs_type = vcs_utils.detect_vcs_type_from_source(source_spec)

        if vcs_type is None:
            self.log("SourceTracker.checkout(): unknown vcs type: %s" % source_spec)
            return None

        backend        = VCSBackendFactory.get_backend(project_type = vcs_type,
                                                       logger       = self.logger)
        project_folder = backend.checkout(source_spec, *rest)

        #
        # TODO:
        #   - attempt to determine tags, if it's github or another site that supports blurbs

        tags        = []
        tags       += self._getTagsFromProjectFolder(tags, project_folder)

        description = None

        self.setTagInfo(source_spec, tags, description)

        self.log()

        return project_folder


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
                raise Exception("multiple tracking links - expected one", trackingLinks)
                # xxx
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
    

    def updateProject(self, project_path, verbose = False):
        """

        """

        if verbose:
            self.log("SourceTracker.updateProject(): %s" % project_path)
            pass
        
        project  = Project(project_path, self)
        result   = project.update()

        if result is not None and result != 0:
            self.log("  result: %s - %s\n" % ( project_path, result, ))
            # XXX only if something happened
            self.log()
            pass

        return result

    
    def updateFolder(self, folder, verbose = False):
        """
        update a folder and any projects below it

        assumes that folder is in the "real" source tree (vs tracking tree)

        """

        vcs_type = vcs_utils.determine_vcs_type(project_path = folder)

        if vcs_type:

            if self._prob is not None and random.random() > self._prob:
                # self.log("  skipping (not sampled): %s" % folder)
                return "skipped"
            
            return self.updateProject(folder, verbose = verbose)

        children = os.listdir(folder)

        for child in children:
            path = os.path.join(folder, child)
            if os.path.isdir(path):
                result = self.updateFolder(path, verbose = verbose)
                pass
            pass

        return
        

    def findProjectsUnderFolder(self, folder):

        # print("findProjectsUnderFolder(): %s" % ( folder, ))
        
        if isinstance(folder, list):
            for _folder in folder:
                for project in self.findProjectsUnderFolder(_folder):
                    yield project
                    pass
                pass
            return

        #
        # determine if it's a project
        #
        vcs_type = vcs_utils.determine_vcs_type(project_path = folder)

        if vcs_type:
            # print("    it's a project: %s - %s" % ( vcs_type, folder, ))
            yield folder
            return

        #
        # not a project.  find children
        #
        children = os.listdir(folder)

        for child in children:
            childFolder = os.path.join(folder, child)
            for project in self.findProjectsUnderFolder(childFolder):
                yield project
                pass
            pass

        return


    def sampleProjects(self, projects, sampleProb):
        """
        TODO: move outward - general
        """
        
        for project in projects:
            if random.random() <= sampleProb:
                yield project
                pass
            pass
        
        return
    
    
    def updateAll(self, verbose = False):
        """
        update all projects under the root tracking folder

        """

        projects = self.findProjectsUnderFolder(self.tracking_folder)

        if self._sampleProb is not None:
            self.log("  using sampling probability %s" % self._sampleProb)

            # TODO: shuffle, to remove bias toward earlier projects, if limiting number
            #       of projects (but then re-sort to original order
            #       after sampling)
            
            projects = self.sampleProjects(projects, self._sampleProb)
            pass

        for project in projects:

            # TODO: put this under some verbosity flag - i sometimes need to find some
            #       repo that must have switched to private, and causes update to
            #       stall (with a pop-up dialog to allow git to use my keychain github
            #       password - i don't have keychain set up)
            print("  updating: %s" % project)

            self.updateProject(project, verbose = verbose)
            pass
            
        return
        

    # XXX weird py 2 vs 3 issue - the commented-out version (which seems fine) is a syntax error in 2.7
    # def update(self, *projects, verbose = False):
    def update(self, *projects, **kwargs):
        """update some or all projects that have been previously tracked

        projects, if supplied, is a list of paths, which may or may
        not be under tracking tree, and might be parent folders (and
        thus not really projects)

        TODO: better to get a stream of real projects, and optionally filter
              (and maybe stall)

        """

        verbose = kwargs.get("verbose")
        
        self.log()
        self.log("start tacker update")
        self.log()

        # TODO: get stream of all projects
        
        if projects:

            # convert from tuple to list
            projects = list(projects)
            projects = self.findProjectsUnderFolder(projects)

            # project at this point is just a sequence of folders
            for project in projects:
                result = self.updateProject(project, verbose = verbose)
                pass
            pass
        else:
            self.updateAll(verbose = verbose)
            pass
        
        self.log()
        self.log("# %s - finished tacker update" % datetime.datetime.today().strftime("%Y%m%d-%H:%M"))
        self.log()

        return


    def _get_vcs_child(self, folder):
        """

        XXX this is not our problem
        """

        # TODO: need to also support hg, svn, ...

        tail      = os.path.basename(folder)
        vcs_child = os.path.join(folder, "git", tail)
                
        if os.path.exists(vcs_child):
            return vcs_child
                
        return None
    
        
    def getProjects(self, folder, patterns = None, depth = None):
        """
        generate stream of all Projects at and below folder

        note: uses tracking/ as root of search - won't find projects that
              are not being tracked

        TODO: generalize - if someone is passing in patterns, then base folder
              does not matter
        """

        # print("# getProjects: %s (depth: %s)" % ( folder, depth ))
        
        if patterns:

            # base_folder = folder
            
            # print("getProjects(): %r, %r" % ( folder, patterns ))

            # pwd = os.getcwd()
            # print("  pwd: %s" % pwd)
            # 
            # i = pwd.find("/src/")
            # 
            # if i != -1:
            #    path_from_base = pwd[i+5:]
            # else:
            #    xxx
            #    pass

            # need tracking folders
            # TODO: support globbing
            # folders = [ os.path.join(base_folder, path_from_base, _folder) for _folder in patterns ]
            folders = patterns
            
            for folder in folders:

                # XXX cheating.  clean this up.  this grossness is an
                #     artifact of the extra folder to indicate source
                #     checkout, vs working with a specific tar.gz

                vcs_child = self._get_vcs_child(folder)

                if vcs_child is not None:
                    folder = vcs_child
                    pass

                try:
                    yield Project(folder, self)
                except NotAProjectException:
                    print("  XXX not a project: %s" % folder)
                    pass
                pass
            return
        
        # note: we can't just check if it's a folder - has to be parseable as a real project
        try:
            yield Project(folder, self)

            # can't have sub-Projects, right?
            return
        except NotAProjectException:
            pass

        #
        # folder was not a project.  dive in to children to find projects
        #
        if depth is not None:
            nextDepth = depth - 1

            if nextDepth < 0:
                return
        else:
            nextDepth = None

        children = os.listdir(folder)
            
        for child in children:

            if child == ".git":
                continue
            
            # XXX maybe a bad idea to put src/tracking under src/
            if child == "tracking":
                continue
                
            childFolder = os.path.join(folder, child)

            # print("#   child: %s" % childFolder)

            if os.path.isdir(childFolder):
                for project in self.getProjects(childFolder, depth = nextDepth):
                    yield project
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
        """start tracking the full set of source urls dumped from another
        instance of oompa
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

    # XXX same stupid 2 vs 3 problem
    # def findProjects(self, *patterns, depth = None):
    def findProjects(self, *patterns, **kwargs):
        """
        simple grep over source tree folders/files

        TODO: breadth first, bail early - currently does depth-first
        TODO: getProjects supports a patterns parameter
        """

        depth      = kwargs.get("depth")
        
        re_pattern = "|".join([ ".*?%s" % pattern for pattern in patterns ])
        regex      = re.compile(re_pattern, re.IGNORECASE)

        # if depth is not None:
        #    depth += 1
        
        for project in self.getProjects(self.tracking_folder, depth = depth):
            if regex.match(project.path) is not None:
                yield project
                pass
            pass
        
        return

    
    def getTagInfo(self, project):
        return self._tag_mgr.getTagInfo(project)

    def getTagInfos(self, *patterns):
        return self._tag_mgr.getTagInfos(*patterns)

    
    def setTagInfo(self, key, tags, description = None):
        """
        key is the source_spec (e.g., https://github.com/....git")
        """

        # print("# SourceTracker.setTagInfo(): %r, %r, %r" % ( key, tags, description ))

        if description is None:

            description = "???"

            # XXX cheating - generalize this to a set of agents who can help

            if key.find("github.com") != -1:

                from oompa.tracking.github.GitHubTracker import GitHubTracker

                # needs to be "the project url", not the .git url
                if key.endswith(".git"):
                    key = key[:-4]
                    pass

                # TODO: memoize
                githubTracker = GitHubTracker(self.config)
                blurb         = githubTracker.githubHelper.getBlurb(url = key)

                # XXX someone else should do all of this
                blurb = blurb.replace("\n", " ")
                if blurb.endswith(" ..."):
                    blurb = blurb[:-4]
                    pass

                if blurb and blurb[0] == "#":
                    blurb = blurb[1:].strip()
                    pass

                while blurb[-1] == "=":
                    blurb = blurb[:-1]
                    pass

                blurb = blurb.strip()
                
                description = blurb
                pass
            pass

        # tag-lookup will be relative to the actual git url
        # XXX need to generalize
        if key.startswith("https://github.com/") and not key.endswith(".git"):
            key = key + ".git"
        
        return self._tag_mgr.setTagInfo(key, tags, description)

    
    def reset_git(self, project_path, verbose = False):
        """special-case (backend-specific) hack, perform a hard reset because
        git can get itself in a knot.

        project_path can be the git folder, or the oompa parent folder

        """


        project  = Project(project_path, self)
        project.setVerbose(verbose)
        result   = project.reset()

        if result is not None and result != 0:
            self.log("  reset_git result: %s - %s\n" % ( project_path, result, ))
            # XXX only if something happened
            self.log()
            pass

        return result
    
    pass
    
