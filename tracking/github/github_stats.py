#
# github_stats.py
#
# TODO:
#   - object, with config setup, for
#

"""
package oompa.tracking.github

"""

import collections
import datetime

from oompa.tracking.github import github_utils


def uniqueRecentContributors(repo):
    """
    repo is a github3 Repository
    """

    # 6 months
    numDays        = 6 * (4 * 7)
    minCommitCount = 20
    today     = datetime.datetime.today()
    startDate = today - numDays * datetime.timedelta(days = 1)

    # note: github3 docs imply that the "number" argument is numWeeks.
    #       i think it's actually numContributors
    numContributors = -1
    
    # contributor object has a contributions field, which is a count.
    # i don't know what the count means
    # for contributor in repo.contributors():
    #    print("      -- %s" % contributor.contributions)

    #
    #
    #
    contributor_statses = repo.contributor_statistics(number = numContributors)

    # trying to understand why the list is sometimes empty
    if contributor_statses.last_status != 0:
        print("  last_status: %s" % contributor_statses.last_status)
        pass

    # { datetime -> [ contributor, ] }
    contributorsByWeek = {}

    committers             = collections.defaultdict(int)
        
    # { contributor }
    committersInPastNWeeks = collections.defaultdict(int)

    
    for contributor_stats in contributor_statses:

        #
        # alt_weeks : [ { "deletions": <int>, 'start of week': <datetime>, 'commits': N, 'additions': N, ...}, ]
        # author:     this user
        # total:      ???
        # weeks:      [{'c': 0, 'w': 1358035200, 'a': 0, 'd': 0}, ...
        #

        contributor = contributor_stats.author

        committers[contributor] += 1
        
        for week_d in contributor_stats.alt_weeks:

            # i don't think we can distinguish "merge commit" (less interesting) from commit.  the github ui does, somehow
            commits = week_d["commits"]

            if not commits:
                continue

            weekStart = week_d["start of week"]
            
            contributorsByWeek.setdefault(weekStart, []).append(contributor)

            if weekStart >= startDate:
                committersInPastNWeeks[contributor] += commits
                pass
            
            # github_utils.dumpSlotValues(contributor_stats)
            pass
        pass

    dumpByWeek = False

    if dumpByWeek:
        weeks = sorted(contributorsByWeek)
        for week in weeks:
            contributors    = contributorsByWeek[week]
            numContributors = len(contributors)
            countStr        = "*" * numContributors
            print("  %s  %3d  %s" % ( week.strftime("%Y%m%d"), numContributors, countStr ))
            pass
        pass

    # TODO: maybe avg committers per week is another interesting stat, distinct enough from total in past N weeks?
    
    # for commit in repo.commits(since = startDate):
    #    print("    commit: %s" % commit)
    #    pass

    enoughCommitsCount = 0
    
    for committer, count in committersInPastNWeeks.items():
        # if count < minCommitCount:
        #    del committersInPastNWeeks[committer]
        #    continue
        if count >= minCommitCount:
            # print("  %3d  %s" % ( count, committer ))
            enoughCommitsCount += 1
            pass
        pass
    
    return {
        "numRecentCommitters"                    : len(committersInPastNWeeks),
        "numRecentCommittersAboveMinCommitCount" : enoughCommitsCount,
        "numCommitters"                          : len(committers),
      }
