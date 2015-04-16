#
# GitHub3Helper.py
#

import json
import os

import github3

from oompa.tracking.github           import github_utils
from oompa.tracking.github.EtagCache import EtagCache


from oompa.tracking.github                       import GitHubMetadataStore

from oompa.tracking.github.EntityMetadataWrapper import EntityMetadataWrapper




class GitHub3Helper:
    """

    sugar around github3

    """

    def __init__(self, config, username = None, password = None):

        self.config = config

        if username is None:
            xxx
            pass

        # XXX
        config_base  = os.environ["HOME"]
        
        gitpass      = open(os.path.join(config_base, "%s.git.passphrase" % username)).read().strip()

        self.github  = github3.login(username, gitpass)

        # XXX needs to go in a work folder
        etags_path   = os.path.join(config_base, "etags.json")
        self.etags   = EtagCache(etags_path)

        # TODO: lazy.  some clients may not need meta at all
        self._metadataStore = GitHubMetadataStore.getGitHubMetadataStore(config, self)
        
        return

    
    def dumpSlots(self, obj):
        """
        list the slots in the specified object

        sugar
        """

        github_utils.dumpSlots(obj)
        return
    
    def dumpSlotValues(self, obj):
        """
        list the slots in the specified object

        sugar
        """
        github_utils.dumpSlotValues(obj)
        return
    
    # dumpList       = github_utils.dumpList

    # def getKindAndName = github_utils.getKindAndName
    

    def me(self):
        return self.github.me()
    

    def checkRatePointsLeft(self):
        """
        return how many "points" (api queries) you have left in the current time window.
        
        normal non-authenticated querying typically has 5000 points refreshed
        every hour

        """
        return self.me().ratelimit_remaining

    
    def getGithubObject(self, name, kind = None):
        """

        """

        # print("GitHub3Helper.getGithubObject(): %s (kind: %s)" % ( name, kind ))

        # if full github url, strip off the prefix
        if name.startswith("https://github.com/"):
            name = name[len("https://github.com/"):]
            pass
        
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

        print("GitHub3Helper.getGithubObject(): %s (kind: %s)" % ( name, kind ))
        print("  no kind specified or obvious, and both user and org are null")
        print("    user: %r" % user)
        print("    org:  %r" % org)
        
        return None



    def getKindNameAndObject(self, args):

        for kind, name in github_utils.getKindAndName(args):
            yield kind, name, self.getGithubObject(name, kind)
            pass

        return


    def getRepos(self,
                 thing,
                 sort     = None,
                 use_etag = True):
        """

        XXX since does not seem to work properly
        TODO: since can be etag or timestamp

        """

        etag = None
        
        if use_etag:
            etag = self.etags.get(thing, "repositories")
            pass
        
        # repos is a GitHubIterator
        #
        # we apparently need to drain the iterator, to get the correct etag
        
        # XXX am i doing something wrong?  why asymmetric apis?
        if thing.type == "Organization":
            repos = thing.repositories(etag = etag)
        else:
            repos = github3.repositories_by(thing.login, etag = etag)
            pass
        
        if sort == "time-newest-first":
            _repos = sorted(repos, key = lambda repo : repo.created_at, reverse = True)
        else:
            _repos = [ repo for repo in repos ]
            pass

        self.etags.set(thing, "repositories", repos.etag)
        
        return _repos



    def list(self, methodName, githubObj, use_etag = True):
        """

        methodName can be anything that returns an iterator
        (repositories, followers, following, ...)

        throws AttributeError if methodName not available on given object

        TODO: if githubObj is a string, get the obj

        """

        method = getattr(githubObj, methodName)
        etag   = None
        
        if use_etag:
            etag = self.etags.get(githubObj, methodName)
            pass

        # print("GitHub3Helper.list(): %s - %s" % ( methodName, githubObj ))
        # print("  etag: %s" % etag)

        iterator = method(etag = etag)
        values   = [ value for value in iterator ]
        
        # TODO: most apis support sorting in the webservice call params
        # if sort == "time-newest-first":
        #    _repos = sorted(repos, key = lambda repo : repo.created_at, reverse = True)
        # else:
        #    _repos = [ repo for repo in repos ]
        #    pass

        # repos is a GitHubIterator
        #
        # we apparently need to drain the iterator, to get the correct etag

        if use_etag:
            self.etags.set(githubObj, methodName, iterator.etag)
            pass
        
        return values

    
    def printRepos(self, thing = None, repos = None, include_readme = True):
        """
        thing can be User or Organization
        """

        if repos is None:
            repos = self.getRepos(thing, sort = "time")
            pass
        
        for repo in repos:

            # dumpSlots(repo, "REPO")
            
            # TODO: instead of updated_at, show N days ago
        
            # print("  repo:     %s %r" % ( repo.last_modified, repo ))

            # XXX
            repo_url = "http://github.com/%s" % repo.full_name
            
            print("  repo:     %s  %s  %s" % ( repo.created_at, repo.updated_at, repo_url ))
            print("")

            # if repo.parent is not None:
            # print("    forked:")
            print("      parent: %s" % repo.parent)
            print("      source: %s" % repo.source)
            print("")
            # pass
            
            if include_readme:

                try:
                    readme_content = repo.readme().decoded

                    if readme_content:
                        # XXX not sure about best way to handle this
                        readme_content = readme_content.decode("utf-8")
                        # print(readme_content.encode("utf-8"))
                    
                        if readme_content:
                            i = readme_content.find("\n\n")
                            if i:
                                readme_content = readme_content[:i] + "\n..."
                                pass
                            pass
                        try:
                            print(readme_content)
                        except UnicodeEncodeError:
                            print(readme_content.encode("utf-8"))
                            pass
                        pass
                    else:
                        print("    no readme yet")
                        pass
                    print("")
                    pass
                except github3.exceptions.ForbiddenError:
                    print("XXX readme access forbidden ???")
                    pass
            # weekly_commit_count is dictionary of { "owner" : [ 0, 0, 1, 0, ... ], "all" : [ 2, 0, 5, ... ] }
            # i think that each is 52 weeks
            
            # print("    commit_count: %s" % repo.weekly_commit_count())
        
            # only at a certain verbosity
            # for contributor in repo.contributors():
            #    print("    contributor: %s" % contributor)
            #    pass
        
            pass

        return


    def getEntityMetadata(self, githubObj):

        print("getEntityMetadata(): %r" % githubObj)

        # github_utils.dumpSlots(githubObj, private = True)

        # XXX hack

        print("Github3Helper.getEntityMetadata - %s - %s" % ( githubObj.name, githubObj.type ))

        # XXX just leave it - don't lower()
        kind = githubObj.type.lower()
        
        # if hasattr(githubObj, "owner"):
        if githubObj.type == "Repository":
            kind = "repository"
            name = "%s/%s" % ( githubObj.owner, githubObj.name )
        else:
            xxx
            pass

        return self._metadataStore.getEntityMetadata(kind, name)


    def getEntityMetadataWrapper(self, githubObj):

        entityMetadata = self.getEntityMetadata(githubObj)
        
        return EntityMetadataWrapper(githubObj, entityMetadata, self)


    def getEntityMetadatas(self, *names, mustExist = True):

        return self._metadataStore.getEntityMetadatas(*names, mustExist = mustExist)

    
    
    pass
    


