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
import sys
import time

from datetime import datetime

from oompa.tracking.github               import github_utils
from oompa.tracking.github.GitHub3Helper import GitHub3Helper

from oompa.tracking.TagManager           import TagManager


class GitHubTracker:
    """
    support for tracking users, organizations, fork trees, etc.
    """
    
    
    def __init__(self, config):
        """
        XXX what is config?
        TODO: need a log
        """

        self.config         = config
        self.githubHelper   = GitHub3Helper(config)

        # XXX mid-refactor.  this should be more invisible
        self._metadataStore = self.githubHelper._metadataStore
        
        return


    def getGithubURL(self, tail):

        return "https://github.com/%s" % tail


    
    def getHTMLAnchorText(self, name):

        url  = self.getGithubURL(name)
        
        return '<a href="%s" target="_blank">%s</a>' % ( url, name )


    def _showEntityTags(self, entityMetadata):
        """
        report tags and description for the given entity in to the report output stream
        """
        
        self.out_stream.write("\n")

        entity_url = entityMetadata.getGithubURL()
        tagInfo    = self._tag_mgr.getTags(entity_url)

        if tagInfo is not None:

            tags, description = tagInfo

            # same output whether html or text (for now)
            # self.out_stream.write("  tags: %s\n" % ( " ".join(tags), ))
            # self.out_stream.write("  desc: %s\n" % ( description, ))

            self.out_stream.write("  tags: %s   desc: %s\n" % ( " ".join(tags), description ))
            
        else:
            self.out_stream.write("  no tag info yet\n")

        self.out_stream.write("\n")
        return
    
    
    def showEntity(self, entityMetadata):
        """
        entityMetadata is an oompa.tracking.github.EntityMetadata
        """
        
        if self._showed_entity:
            return
        
        if self._format == "html":
            self.out_stream.write("GitHub entity: %s - %s\n" % (  entityMetadata.kind, self.getHTMLAnchorText(entityMetadata.name), ))
        else:
            print("GitHub entity: %-25s (%s)" % ( entityMetadata.name, entityMetadata.kind ))

        self._showEntityTags(entityMetadata)
        
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

        # newValue will be a list of Repository objects
        newValue = self.githubHelper.list(field, github_obj)

        # print("reportListUpdates: %s - %s" % ( entityMetadata.name, field, ))
        # print("   new: %r" % newValue)
        
        if not newValue:
            return False
        
        prevValue = entityMetadata.setdefault(field, [])

        # XXX the lack of writer framework hurts here
        if self._format == "html":
            format_link = self.getHTMLAnchorText
        else:
            format_link = self.getGithubURL

        # note: i think that newalue is a list of Repository and prevValue is a list of strings

        if valueAttr is not None:

            # TODO: unroll this, to report which objects have the empty value
            newValue = [ getattr(value, valueAttr) for value in newValue ]

            if "" in newValue:
                print("  removing empty strings from newvalue - %s" % ( field, ))
                newvalue = [ value for value in newValue if value != '' ]
                pass

            # print("NV: %r" % newValue)
            pass

        # ( addedValues, removedValues )
        #    both are sets

        if "" in prevValue:
            print("  diffLists - empty in prevValue (i.e., they were stored in db): %r\n" % prevValue)
            prevValue = [ value for value in prevValue if value != '' ]
            pass
        
        diffs = entityMetadata.getListDiffs(newValue,
                                            prevValue)

        # note that we don't yet render the sets.  it just to determine if we want to
        # show the section header
        
        if diffs[0] or diffs[1]:
            self.showEntity(entityMetadata)

        if diffs[0] or diffs[1]:
            entityMetadata.diffLists(field,
                                     newValue,
                                     prevValue,
                                     out_stream  = self.out_stream,
                                     format_link = format_link)
            # just because i'm impatient
            self.out_stream.flush()

        entityMetadata.updateList(field, newValue)

        return
                


    def filterMetadatas(self, entityMetadatas, patterns):
        """
        only yield entities that string-match lower-case
        TODO: get more clever - globbing

        """

        patterns = [ pattern.lower() for pattern in patterns ]

        for entityMetadata in entityMetadatas:
            entityNameLower = entityMetadata.name.lower()
            for pattern in patterns:
                if entityNameLower.find(pattern) != -1:
                    yield entityMetadata
                    break
                pass
            pass

        return
        
        
    def listTracking(self, patterns = None):
        """
        yield some or all github entities (users, orgs) currenty being tracked

        if patterns specified, only yield entities that string-match lower-case

        """

        entityMetadatas = self.githubHelper.getEntityMetadatas(mustExist = False)
            
        if patterns:
            entityMetadatas = self.filterMetadatas(entityMetadatas, patterns)
            pass

        for entityMetadata in entityMetadatas:
            yield "%s/%s" % ( entityMetadata.kind, entityMetadata.name )
            pass

        return


    def getGithubObject(self, entityMetadata):

        return self.githubHelper.getGithubObject(entityMetadata.name,
                                                 entityMetadata.kind)
    

    def printRatePointsLeft(self, message):
        """sugar
        """
        self.githubHelper.printRatePointsLeft(message)
        return



    def discoverHtmlFormat(self, *args, verbose = False):

        self._tag_mgr  = TagManager(self.config,
                                    tags_filename = "entity-tags.tsv")

        today_yyyymmdd = datetime.today().strftime("%Y%m%d")
        
        # XXX allow caller to override defaults
        dest_folder    = os.path.join(os.environ["HOME"], "oompa", "discover")
        out_path       = os.path.join(dest_folder, "%s.discover.html" % today_yyyymmdd)

        # TODO: make sure folder exists
        
        # set this to False if you want to be able to re-run discover from last snapshot
        # XXX get from config
        
        update_metadata = True
        # update_metadata = False

        if not update_metadata:
            print("  *not* flushing entity meta updates yet")

        print("writing to: %s" % out_path)

        self.out_stream = open(out_path, "w", encoding = 'utf8')

        out_stream = self.out_stream
        
        out_stream.write('<!DOCTYPE html>\n')
        out_stream.write('<meta charset="utf-8">\n')
        out_stream.write('<html>\n')
        out_stream.write('<head>\n')
        out_stream.write('<title>Tracker Discover Report - %s</title>\n' % ( today_yyyymmdd, ))
        out_stream.write('</head>\n')

        out_stream.write('<body>\n')

        # XXX temp
        out_stream.write('<pre>\n')
        
        helper = self.githubHelper

        # TODO: pass in an option, maybe a threshold based on number
        #       of repos?  this is about rate limit problems for
        #       certain entities

        if args:
            print("# not showing initial repos - stil trying to figure out rate limit problem for some entities")
            showRepos = False
        else:
            showRepos = True

        for entityMetadata in helper.getEntityMetadatas(*args, mustExist = False):

            #
            # there are several places which may show the entity the
            # first time.  we only want to show once
            #
            self._showed_entity = False

            print("# %-40s (%s)" % ( entityMetadata.name, entityMetadata.kind ))

            if verbose:
                self.printRatePointsLeft("  rate points before checking entity")

            github_obj  = self.getGithubObject(entityMetadata)
            repos       = helper.getRepos(github_obj, sort = "time-newest-first")

            # TODO: switch to generic listing
            # TODO: support for filtering *anything* through already-known
            knownRepos  = entityMetadata.setdefault("repoNames", [])
            newRepos    = [ repo for repo in repos if repo.full_name not in knownRepos ]

            if newRepos:
                self.showEntity(entityMetadata)
                out_stream.write("  %d new repos\n" % len(newRepos))
                if showRepos:
                    out_stream.write("\n")
                    helper.printRepos(repos       = newRepos,
                                      out_stream  = out_stream,
                                      format_link = self.getHTMLAnchorText)
                pass

            # TODO: lift this in to the above clause
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

            if update_metadata:
                entityMetadata.flush()

            if self._showed_entity:
                out_stream.write("\n")
                
            pass

        out_stream.write('</pre>\n')
        out_stream.write('</body>\n')
        out_stream.write('</html>\n')

        if out_stream != sys.stdout:
            out_stream.close()
            pass
        
        return

    
    
    def discover(self, *args, format = None, verbose = False):
        """either add new github entities (users/groups) to the set you
        are tracking (if you specify args), or get an update on the
        entities you are already tracking

        """

        # XXX should use a Writer framework, but i don't expect this to live long - will
        #     go to a db and web server soon

        # XXX cheating
        self._format = format
        
        if format == "html":
            self.discoverHtmlFormat(*args, verbose = verbose)
            return

        # XXX temp
        # self.out_stream = sys
        
        helper = self.githubHelper

        # TODO: pass in an option, maybe a threshold based on number
        #       of repos?  this is about rate limit problems for
        #       certain entities

        if args:
            print("# not showing initial repos - stil trying to figure out rate limit problem for some entities")
            showRepos = False
        else:
            showRepos = True

        for entityMetadata in helper.getEntityMetadatas(*args, mustExist = False):

            # XXX
            self._showed_entity = False

            if verbose:
                self.showEntity(entityMetadata)
                self.printRatePointsLeft("  rate points before checking entity")
                pass

            github_obj  = self.getGithubObject(entityMetadata)
            repos       = helper.getRepos(github_obj, sort = "time-newest-first")

            # TODO: switch to generic listing
            # TODO: support for filtering *anything* through already-known
            knownRepos  = entityMetadata.setdefault("repoNames", [])
            newRepos    = [ repo for repo in repos if repo.full_name not in knownRepos ]

            if newRepos:

                self.showEntity(entityMetadata)

                print("  %d new repos" % len(newRepos))

                if showRepos:
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


    def removeEntities(self, entities):
        """entities is list of entity specs - user/...,
        org[anization]/..., or un-qualified entity name

        """

        return self.githubHelper.removeEntities(entities)
        
    pass


