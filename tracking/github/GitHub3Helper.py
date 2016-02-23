#
# GitHub3Helper.py
#
#
# TODO: User, Organization, Repository instead of user, org, repo
# TODO: totally remove "repo"

import json
import os
import sys       # XXX use logging system, instead of sys.stderr
import time

# for readme-cleaning
import re       

import github3

from oompa.tracking.github                       import github_utils
from oompa.tracking.github                       import GitHubMetadataStore
from oompa.tracking.github.EtagCache             import EtagCache
from oompa.tracking.github.EntityMetadataWrapper import EntityMetadataWrapper



def extractBlurb(content):
    """

    TODO: move to some text-processing home
    TODO: can indicate the number of lines
    """

    if not content:
        return content

    # XXX if it's still bytes, then it was not utf8, and we won't be able to split it
    if isinstance(content, bytes):
        return content
    
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



# TODO: be lazy about the regex
# TODO: have to update to support just one-square-one-paren
badgePattern = '(\[\!\[.*?\].*?\]\(.*?\))'
badgeRegex   = re.compile(badgePattern)



def removeStinkinBadges(line):
    """a lot of github readmes have a row of "badges" on the first line
    (e.g., to indicate that it's green/red in
    jenkins/travis/bamboo/whatever, to indicate code coverage, ...)

    '# spritezero-cli\n\n[![build status](https://secure.travis-ci.org/mapbox/spritezero-cli.svg)](http://travis-ci.org/mapbox/spritezero-cli) [![Coverage Status](https://coveralls.io/repos/mapbox/spritezero-cli/badge.svg?branch=master&service=github)](https://coveralls.io/github/mapbox/spritezero-cli?branch=master)\n...'

    '# untiler\n\n[![Build Status](https://magnum.travis-ci.com/mapbox/untiler.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master)](https://magnum.travis-ci.com/mapbox/untiler) [![Coverage Status](https://coveralls.io/repos/mapbox/untiler/badge.svg?branch=master&service=github&t=nhModO)](https://coveralls.io/github/mapbox/untiler?branch=master)\n...'

    for the purposes of discovery in a shell, that is not helpful

    they are generally easy to spot and remove

      [![label](url)](url)

    """

    return badgeRegex.sub("", line)


    
def test_removeStinkinBadges():

    # note: these lines are originally bytes, from the webservice.  i am just
    #       focusing on the strings, since we decode the bytes

    line         = '[![build status](https://secure.travis-ci.org/mapbox/spritezero-cli.svg)](http://travis-ci.org/mapbox/spritezero-cli)'
    scrubbedLine = removeStinkinBadges(line)

    assert scrubbedLine == ""

    # conntent before and after.  no newlines yet
    line         = 'spritezero-cli [![build status](https://secure.travis-ci.org/mapbox/spritezero-cli.svg)](http://travis-ci.org/mapbox/spritezero-cli) something after'
    scrubbedLine = removeStinkinBadges(line)

    assert scrubbedLine == 'spritezero-cli  something after'


    line = '# spritezero-cli\n\n[![build status](https://secure.travis-ci.org/mapbox/spritezero-cli.svg)](http://travis-ci.org/mapbox/spritezero-cli) [![Coverage Status](https://coveralls.io/repos/mapbox/spritezero-cli/badge.svg?branch=master&service=github)](https://coveralls.io/github/mapbox/spritezero-cli?branch=master)\n...'

    scrubbedLine = removeStinkinBadges(line)
    
    assert scrubbedLine == '# spritezero-cli\n\n \n...'

    # nearly the same, just different urls for build and coverage status
    line = '# untiler\n\n[![Build Status](https://magnum.travis-ci.com/mapbox/untiler.svg?token=Dkq56qQtBntqTfE3yeVy&branch=master)](https://magnum.travis-ci.com/mapbox/untiler) [![Coverage Status](https://coveralls.io/repos/mapbox/untiler/badge.svg?branch=master&service=github&t=nhModO)](https://coveralls.io/github/mapbox/untiler?branch=master)\n...'

    scrubbedLine = removeStinkinBadges(line)

    assert scrubbedLine == '# untiler\n\n \n...'

    return


# test_removeStinkinBadges()
    


class GitHub3Helper:
    """

    sugar around github3

    """

    def __init__(self, config, username = None, password = None):
        """
        XXX what is config?  currently just a dict
        """

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
    

    def me(self):
        return self.github.me()
    

    def checkRatePointsLeft(self):
        """return how many "points" (api queries) you have left in the
        current time window.
        
        normal non-authenticated querying typically has 5000 points
        refreshed every hour

        """
        return self.me().ratelimit_remaining


    def printRatePointsLeft(self, message):
        print("%s: %s" % ( message, self.checkRatePointsLeft() ))
        return

    
    def getGithubObject(self, name, kind = None):
        """

        """

        # print("GitHub3Helper.getGithubObject(): %s (kind: %s)" % ( name, kind ))

        # if full github url, strip off the prefix
        if name.startswith("https://github.com/"):
            name = name[len("https://github.com/"):]
            pass

        # XXX i think we need to replace http://github.com with https://github.com
        
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

        thing is XXX what?

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

        if use_etag:
            self.etags.set(thing, "repositories", repos.etag)
            pass
        
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

                
    def getReadmeContent(self, repo = None, url = None):
        """
        attempts to return string
        """

        if repo is None:
            repo = self.getGithubObject(url, kind = "repo")
            pass
        
        try:
            readme_content = repo.readme().decoded
        except:
            return ""

        # print("getReadmeContent(): %r - %r" % ( readme_content, type(readme_content) ))
        
        # if readme_content is not None:
        if readme_content:
            # XXX 20150824 - started getting utf8 UnicodeDecodeError, on Netflix-SkunkWorks
            try:
                # readme_content = readme_content.decode("utf-8")
                readme_content = readme_content.decode()
                # print("# ... decoded")
                readme_content = removeStinkinBadges(readme_content)
                # print("# ... removed badges")
            except UnicodeDecodeError:
                # print("# ... UnicodeDecodeError")
                pass
            pass

        # print("  final: %r - %r" % ( readme_content, type(readme_content) ))
        
        return readme_content

    
    def getBlurb(self, repo = None, url = None):
        """
        note that this may return bytes or a string
        """
        
        readme_content = self.getReadmeContent(repo = repo, url = url)

        if readme_content is None:
            return "no readme yet"

        blurb = extractBlurb(readme_content)

        return blurb

                
    def printRepos(self,
                   thing = None,
                   repos          = None,
                   include_readme = True,
                   out_stream     = None,
                   format_link    = None):
        """thing can be User or Organization

        if include_readme is true, will try to report a decent blurb
        from the top of the readme as a clue about the project

        """

        if out_stream is None:
            out_stream = sys.stdout
        
        if repos is None:
            repos = self.getRepos(thing, sort = "time")
            pass

        # experiment with avoiding rate limit crashes
        stall = None
        # stall = 1.0

        if stall:
            print("# stalling %s sec between each repo, to try to avoid rate limit problems" % stall)

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

            # XXX always use format_link - EntityMetadata has getGithubURL - refactory

            if format_link:
                repo_url = format_link(repo.full_name)
            else:
                # XXX
                repo_url = "https://github.com/%s" % repo.full_name
                pass
            
            out_stream.write("  repo:     %s  %s  %s\n" % ( repo.created_at, repo.updated_at, repo_url ))
            out_stream.write("\n")

            # need to do this to pull in proper "pedigree" (forked from, ...)
            repo.refresh()
            
            if repo.parent is not None:
                out_stream.write("      forked: %s\n" % repo.parent)

                if repo.source != repo.parent:
                    print("      source: %s" % repo.source)
                    pass
                out_stream.write("\n")
                pass
            
            if include_readme:

                blurb = self.getBlurb(repo)
                
                # if isinstance(blurb, bytes):

                if not blurb:
                    blurb = ""
                    
                out_stream.write(blurb)
                # else:
                #    out_stream.write(blurb.encode("utf-8"))
                #    pass

                out_stream.write("\n")
                out_stream.write("\n")
                pass

            # weekly_commit_count is dictionary of { "owner" : [ 0, 0, 1, 0, ... ], "all" : [ 2, 0, 5, ... ] }
            # i think that each is 52 weeks
            
            # out_stream.write("    commit_count: %s\n" % repo.weekly_commit_count())
        
            # only at a certain verbosity
            # for contributor in repo.contributors():
            #    out_stream.write("    contributor: %s\n" % contributor)
            #    pass

            if stall:
                time.sleep(stall)
                pass
            pass

        return


    def getEntityMetadata(self, githubObj):
        """
        
        XXX returns what?
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
    
