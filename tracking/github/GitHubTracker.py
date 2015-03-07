#
# GitHubTracker.py
#

"""
package oompa.tracking.github

  XXX wrong home

support for 
"""

import json
import os

from oompa.tracking.github               import github_utils
from oompa.tracking.github.GitHub3Helper import GitHub3Helper


class GitHubTracker:
    """
    support for tracking users, organizations, fork trees, etc.
    """
    
    _kinds = [ "User", "Organization" ]
    
    def __init__(self, config, username = None):
        """
        TODO: need a log
        """

        # XXX get everything from config
        
        self.root = os.path.join(os.environ["HOME"], "src", "github")

        if username is None:
            xxx
            pass

        self.githubHelper = GitHub3Helper(config, username)
        
        return


    def getFolder(self, kind, name):

        return os.path.join(self.root, kind.lower(), name)

    
    def findEntityFolder(self, name):

        for kind in self._kinds:
            folder = self.getFolder(kind, name)
            if os.path.exists(folder):
                return folder
            pass

        return None
        
    def createFolder(self, kind, name):

        folder = self.getFolder(kind, name)

        if os.path.exists(folder):
            return

        os.mkdir(folder)

        return folder
        
    
    def _getMetadataPath(self, folder):

        return os.path.join(folder, "tracker.meta.json")


    
    def _getEntityMetadata(self, folder):

        metadataPath = self._getMetadataPath(folder)
        
        # TODO: need to wrap the json
        
        if os.path.exists(metadataPath):
            return json.load(open(metadataPath))

        return {}

    def _saveEntityMetadata(self, folder, metadata):

        metadataPath = self._getMetadataPath(folder)

        if not os.path.exists(folder):
            xxx
            pass

        file = open(metadataPath, "w")
        json.dump(metadata, file)
        file.close()

        return
    
    
    def discover(self, *args):

        helper = self.githubHelper
        
        # try to find in /user or /organization

        for name in args:

            folder = self.findEntityFolder(name)
            
            if folder is None:

                github_obj = helper.getGithubObject(name)

                if github_obj:
                    print("    github_obj: %s - %r" % ( github_obj.type, github_obj ))
                    # helper.dumpSlotValues(github_obj)

                    folder = self.createFolder(github_obj.type, name)

                    print("  created folder: %s" % folder)
                else:
                    print("    name not found (user or org): %s" % name)
                    pass
                pass
            else:
                kind       = os.path.basename(os.path.dirname(folder))
                github_obj = helper.getGithubObject(name, kind)
                pass
            
            print("GitHubTracker.discover(): %-20s %s" % ( name, folder ))

            entityMetadata = self._getEntityMetadata(folder)
            since          = entityMetadata.get("etag")

            # if since:
            #    print("   using since: %s" % since)
            #    pass
            
            repos     = helper.getRepos(github_obj,
                                        sort  = "time-newest-first",
                                        since = since)


            knownRepos = entityMetadata.setdefault("repoNames", [])
            newRepos   = [ repo for repo in repos if repo.full_name not in knownRepos ]

            if newRepos:
                helper.printRepos(repos = newRepos)
            else:
                print("  no new repos")
                pass

            # print("  etag %s - %s  %s" % ( github_obj.type, name, github_obj.etag ))

            # saving should be transparent

            changed = False
            
            if github_obj.etag != entityMetadata.get("etag"):
                entityMetadata["etag"]      = github_obj.etag
                changed = True
                pass

            if newRepos:
                for repo in newRepos:
                    entityMetadata["repoNames"].append(repo.full_name)
                    pass
                changed = True
                pass

            if changed:
                self._saveEntityMetadata(folder, entityMetadata)
                pass
            
            pass
        
        return

    pass


