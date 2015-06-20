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
    
    
    def __init__(self, config, username = None):
        """
        TODO: need a log
        """

        if username is None:
            xxx
            pass

        self.githubHelper   = GitHub3Helper(config, username)

        # XXX mid-refactor.  this should be more invisible
        self._metadataStore = self.githubHelper._metadataStore
        
        return

    

    def showEntity(self, entityMetadata):

        if self._showed_entity:
            return

        print("GitHubTracker.discover(): %-25s (%s)" % ( entityMetadata.name, entityMetadata.kind ))
        
        self._showed_entity = True

        return
    

    def reportListUpdates(self, field, github_obj, entityMetadata, valueAttr):

        # XXX be more focused
        # use_etag = True
        # use_etag = False
        # if not use_etag:
        #    print("# not using etag in GitHubTracker.reportListUpdates()")
        #    pass
        # newValue = self.githubHelper.list(field, github_obj, use_etag = use_etag)

        newValue = self.githubHelper.list(field, github_obj)

        # print("reportListUpdates: %s - %s" % ( name, field ))
        # print("   new: %s" % newValue)
        
        if not newValue:
            return False
        
        self.showEntity(entityMetadata)

        prevValue = entityMetadata.setdefault(field, [])
        
        entityMetadata.diffLists(field, newValue, prevValue, valueAttr)

        entityMetadata.updateList(field, newValue, valueAttr)

        return
                

    def listTracking(self):

        for entityMetadata in self.githubHelper.getEntityMetadatas(mustExist = False):
            yield "%s/%s" % ( entityMetadata.kind, entityMetadata.name )
            pass

        return

    
    def discover(self, *args, verbose = False):
        """either add new github entities (users/groups) to the set you
        are tracking (if you specify args), or get an update on the
        entities you are already tracking

        """

        helper        = self.githubHelper
        
        for entityMetadata in helper.getEntityMetadatas(*args, mustExist = False):

            # XXX
            self._showed_entity = False

            if verbose:
                self.showEntity(entityMetadata)
                pass

            # XXX this has to happen differently now
            # if folder is None:
            #    print("    name not found (user or org): %s" % name)
            #    continue

            name = entityMetadata.name
            kind = entityMetadata.kind
            
            github_obj     = helper.getGithubObject(name, kind)
            
            repos          = helper.getRepos(github_obj,
                                             sort  = "time-newest-first")

            # TODO: switch to generic listing
            # TODO: support for filtering *anything* through already-known
            knownRepos     = entityMetadata.setdefault("repoNames", [])
            newRepos       = [ repo for repo in repos if repo.full_name not in knownRepos ]

            if newRepos:

                self.showEntity(entityMetadata)

                print("  %d new repos" % len(newRepos))
                helper.printRepos(repos = newRepos)
                pass

            if newRepos:
                for repo in newRepos:
                    entityMetadata.append("repoNames", repo.full_name)
                    pass
                pass

            # XXX organizations have followers_count and following_count, but no
            #     followers() or following()

            if github_obj.type == "User":

                self.reportListUpdates("followers",            github_obj, entityMetadata, "login")
                self.reportListUpdates("following",            github_obj, entityMetadata, "login")
                self.reportListUpdates("starred_repositories", github_obj, entityMetadata, "full_name")
                
            elif github_obj.type == "Organization":

                self.reportListUpdates("public_members", github_obj, entityMetadata, "login")

                pass

            entityMetadata.flush()
            
            pass
        
        return

    pass


