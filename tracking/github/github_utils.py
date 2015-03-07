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
    



def getKindAndName(args):

    for name in args:

        if "/" in name:
            yield "repo", name
            continue
        
        if ":" in name:
            kind, name = name.split(":")
        else:
            # TODO: try both - if user exists, return it, else try org (and maybe crash)
            kind = "user"
            pass
        
        yield kind, name
        pass

    return
