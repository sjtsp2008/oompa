#
#
#

"""
TODO: support for metering
  - "that just cost 400 points"

"""

import os

import github3

# partial github schemas

# Repository
#   branches()
#   code_frequency()
#   collaborators()
#   commit_actvity()
#   commits()
#   contributor_statistics()
#   contributors()
#   default_branch
#   events()
#   forks_count
#   forks()
#   full_name
#   has_wiki
#   homepage
#   last_modified            always None?
#   master_branch
#   milestones()
#   parent
#   pull_requests()
#   readme()
#   stargazers()
#   stargazers_count
#   subscribers()
#   tags()
#   teams()
#   tree()
#   updated_at
#   watchers                  a count?  (not a method)
#   weekly_commit_count()
#


# User
#
# company - try to link to org/team?
# followers
# following
# iter_orgs()
# iter_starred()
# iter_subscriptions()
# location
# public_gists
# public_repos (count)
# type


# Organization




def dumpSlots(obj, label = None, private = False):
    """
    support in understanding what's available in a python object

    mostly used to understand github things, but is generally useful
    """
    
    print("slots: %s" % label or obj)
    
    slots = dir(obj)

    for slot in slots:

        if not private and slot[0] == "_":
            continue

        suffix = ""

        if callable(getattr(obj, slot)):
            suffix = "()"
            pass

        print("  %s%s" % ( slot, suffix ))
        pass

    return



def dumpSlotValues(obj, label = None, private = False):
    """
    support in understanding what's available in a python object

    if private is False, don't show any slots that start with "_"
    """
    
    print("slots values: %s" % label or obj)
    
    slots     = dir(obj)

    # make it pretty - line things up in columns
    maxLen    = max(map(len, slots))
    formatStr = "  %%-%ds  %%r" % ( maxLen + 3, )
    
    for slot in slots:

        if not private and slot[0] == "_":
            continue

        # TODO: list of regexes to skip
        if slot.startswith("delete_"):
            continue

        if slot.startswith("create_"):
            continue

        if slot.startswith("add_"):
            continue
        
        # print("# slot: %s" % slot)
        
        value  = getattr(obj, slot)

        suffix = ""

        if callable(value):
            suffix = "()"
            slot   = slot + suffix
            # if not (slot.startswith
            # value  = value()
            value = "?"
            pass

        # print("  %s%s   %r" % ( slot, suffix, value ))
        print(formatStr % ( slot, value ))
        pass

    return



def dumpList(obj, slot, pad = 15):
    """
    print the list returned by an object method

      e.g., dumpList(user, "followers")
    """
    
    formatStr = "  %%-%ds  %%s" % pad

    for value in getattr(obj, slot)():
        print(formatStr % ( slot, value ))
        pass

    return
    

#
# support some aliases
#
# note that if an alias is not in here, it maps to itself.  so we don't include
# Repository, ...
#
officialKind_d = {

    "repo" : "Repository",
    "user" : "User",
    "org"  : "Organization",
    
    }


def getKindAndName(args):
    """


    """

    for name in args:

        # support stripping "http://github.com/" from front, in case i
        # pasted in full url from some other tool

        if name.startswith("http://github.com/"):
            name = name[len("http://github.com/"):]
            pass

        if "/" in name:
            yield "Repository", name
            continue
        
        if ":" in name:
            kind, name = name.split(":")
            kind       = officialKind_d.get(kind, kind)
        else:
            # TODO: try both - if user exists, return it, else try org (and maybe crash)
            # kind = "User"
            # kind = "Organization"
            kind = None
            pass
        
        yield kind, name
        pass

    return



def dumpTwoOutFromRepo(repo, githubHelper):
    """
    dumps the one-outs (forked, starred, watching), and then organizes
    two-out (repos, starred, watching, ...)

    TODO: move "the guts" in to helper
    """
    
    print("dumpTwoOutRepo: %s/%s" % ( repo.owner, repo.name ))
    # dumpSlotValues(repo)

    # TODO: want this to be transparent - use-cache-if-recent-else-get-value-and-stash-it

    use_etag    = False
    
    wrapper     = githubHelper.getEntityMetadataWrapper(repo)
    stargazers  = wrapper.useCachedOrGetList("stargazers", use_etag)

    print("%4d stargazers" % len(stargazers))
    
    # for stargazer in stargazers:
    #    print("  gazer: %s" % ( stargazer, ))
    #    pass

    print("")

    # TODO: subscribers

    # TODO: followers, following
    
    #
    # { repo -> [ user, ] }
    #
    starred_by_user = { }

    field = "starred_repositories"
    
    for stargazer in stargazers:

        print("  gazer: %r" % ( stargazer, ))
        
        starred_repos = githubHelper.list(field, stargazer)
        starred_repos = list(starred_repos)

        for repo in starred_repos:
            print("    %s" % repo.name)
            pass
        
        pass
        
    # contributors()?  usually private
    
    return


def dumpTwoOut(obj, kind, helper):

    # XXX maybe don't need this switch, but simpler to keep things separate, initially
    
    if kind == "Repository":
        dumpTwoOutFromRepo(obj, helper)
    else:
        print("  %s - %s" % ( kind, obj.name ))
        pass
    
    return
