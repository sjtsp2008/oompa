#
#
#

import os

import github3


from oompa.tracking.github import github_utils


class GitHub3Helper:
    """

    sugar around github3

    """

    def __init__(self, config, username = None, password = None):

        self.config = config

        if username is None:
            xxx
            pass

        gitpass =     open(os.path.join(os.environ["HOME"], "%s.git.passphrase" % username)).read().strip()

        self.github  = github3.login(username, gitpass)

        return

    
    def dumpSlots(self, obj):
        github_utils.dumpSlots(obj)

    def dumpSlotValues(self, obj):
        github_utils.dumpSlotValues(obj)

    # dumpList       = github_utils.dumpList
    # getKindAndName = github_utils.getKindAndName
    
    
    def getGithubObject(self, name, kind = None):

        if kind is not None:
            kind = kind.lower()
            pass
        
        if kind == "user":
            return self.github.user(name)

        if kind == "org" or kind == "organization":
            return self.github.organization(name)

        if kind == "repo":
            owner, repoName = name.split("/")
            return github3.repository(owner, repoName)

        if kind is not None:
            xxx
            pass
        
        #
        #
        #
        if "/" in name:
            owner, repoName = name.split("/")
            return github3.repository(owner, repoName)
        
        # try both user and org.  if both, panic

        user = self.github.user(name)
        org  = self.github.organization(name)

        if user and org:
            # XXX this needs to be policy
            print("  note: both user and org exist - returning org: %s" % name)
            return org

        if user:
            return user

        if org:
            return org
        
        return None



    def getKindNameAndObject(self, args):

        for kind, name in getKindAndName(args):
            yield kind, name, getGithubObject(name, kind)
            pass

        return


    def getRepos(self,
                 thing,
                 sort       = None,
                 since      = None):
        """

        XXX since does not seem to work properly
        TODO: since can be etag or timestamp

        """

        # print("getRepos: since: %r" % since)
        
        # assuming that since is an etag.  if it's a date, we have to filter
        
        # XXX am i doing something wrong?  why asymmetric apis?
        if thing.type == "Organization":
            repos = thing.repositories(etag = since)
        else:
            repos = github3.repositories_by(thing.login, etag = since)
            pass
        
        if sort == "time-newest-first":
            repos = sorted(repos, key = lambda repo : repo.created_at, reverse = True)
            pass

        return repos

    
    def printRepos(self, thing = None, repos = None):
        """
        thing can be User or Organization
        """

        if repos is None:
            repos = self.getRepos(thing, sort = "time")
            pass
        
        print("%d repos" % len(repos))
            
        for repo in repos:

            # dumpSlots(repo, "REPO")
            
            # TODO: instead of updated_at, show N days ago
        
            # print("  repo:     %s %r" % ( repo.last_modified, repo ))
            print("  repo:     %s  %s  %r" % ( repo.created_at, repo.updated_at, repo.full_name ))
            
            # TODO: need to indicate if it was forked, 
        
            # dictionary of { "owner" : [ 0, 0, 1, 0, ... ], "all" : [ 2, 0, 5, ... ] }
            # print("    commit_count: %s" % repo.weekly_commit_count())
        
            # only at a certain verbosity
            # for contributor in repo.contributors():
            #    print("    contributor: %s" % contributor)
            #    pass
        
            pass

        return


    pass
    


