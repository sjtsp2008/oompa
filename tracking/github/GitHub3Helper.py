#
# GitHub3Helper.py
#
#
# TODO: User, Organization, Repository instead of user, org, repo
# TODO: totally remove "repo"

import json
import os
import sys       # XXX use logging system, instead of sys.stderr

import github3

from oompa.tracking.github           import github_utils
from oompa.tracking.github.EtagCache import EtagCache


from oompa.tracking.github                       import GitHubMetadataStore

from oompa.tracking.github.EntityMetadataWrapper import EntityMetadataWrapper



def extractBlurb(content):
    """

    TODO: move to some text-processing home
    TODO: can indicate the number of lines
    """
    

    if not content:
        return content
    
    # print("extractBlurb(): content: %r" % content)

    paragraphs     = content.split("\n\n")
    numParagraphs  = len(paragraphs)
    firstParagraph = paragraphs[0]

    # print("  paragraphs: %r - %r" % ( numParagraphs, paragraphs ))

    if numParagraphs == 1:
        return firstParagraph
    
    # frequent case that occurs - first paragraph is one line title,
    # and the summary paragraph is the second
    
    lines = firstParagraph.split("\n")

    if len(lines) == 1 and len(lines[0].split()) <=4:
        return "\n\n".join([ firstParagraph, paragraphs[1] ]) + "\n..."
    
    return firstParagraph + "\n..."





class GitHub3Helper:
    """

    sugar around github3

    """

    def __init__(self, config, username = None, password = None):

        self.config = config

        if username is None:
            username = config.get("gituser")

            if username is None:
                username = os.environ.get("GITUSER")

                if username is None:
                    sys.stderr.write("you need to set GITUSER (and make sure that $HOME/<gituser>.git.passphrase contains your github passphrase)")
                    sys.exit(-1)
                    pass
                pass
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
        
        # if kind is not None:
        #    kind = kind.lower()
        #    pass
        
        if kind == "User" or kind == "user":
            return self.github.user(name)

        if kind == "Organization" or kind == "org" or kind == "organization":
            return self.github.organization(name)

        if kind == "Repository" or kind == "repo":
            owner, repoName = name.split("/")
            return github3.repository(owner, repoName)

        if kind is not None:
            print("  kind not recognized: %r" % kind)
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

        sort can be "time-newest-first" or None

        TODO: support need_parent boolean param, so that we can call refresh and no one else has to worry
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

                
    def getReadmeContent(self, repo):

        try:
            readme_content = repo.readme().decoded
        except:
            return None

        if readme_content:
            readme_content = readme_content.decode("utf-8")
            pass

        return readme_content


                
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

            # https://github3py.readthedocs.org/en/master/repos.html
            #
            #    When listing repositories in any context, GitHub
            #    refuses to return a number of attributes, e.g.,
            #    source and parent. If you require these, call the
            #    refresh method on the repository object to make a
            #    second call to the API and retrieve those attributes.

            repo.refresh()
            
            # print("  repo:     %s %r" % ( repo.last_modified, repo ))

            # XXX
            repo_url = "http://github.com/%s" % repo.full_name
            
            print("  repo:     %s  %s  %s" % ( repo.created_at, repo.updated_at, repo_url ))
            print("")

            if repo.parent is not None:
                print("      forked: %s" % repo.parent)

                if repo.source != repo.parent:
                    print("      source: %s" % repo.source)
                    pass
                print("")
                pass
            
            if include_readme:

                readme_content = self.getReadmeContent(repo)

                if readme_content is None:
                    print("    no readme yet")
                else:
                    blurb = extractBlurb(readme_content)

                    print(blurb.encode("utf-8"))
                    
                    # why not just always encode?  i think it's something about bytes vs string?
                    # try:
                    #    print(readme_content)
                    # except UnicodeEncodeError:
                    #    print(readme_content.encode("utf-8"))
                    #    pass
                    pass
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
        """

        """
        
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
        """

        """
        
        return self._metadataStore.getEntityMetadatas(*names, mustExist = mustExist)


    def removeEntities(self, entitySpecs):

        return self._metadataStore.removeEntities(entitySpecs)
        
    pass
    
