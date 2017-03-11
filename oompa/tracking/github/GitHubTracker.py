#
# GitHubTracker.py
#

"""
package oompa.tracking.github

"""

import os
import sys
import time

from datetime import datetime

from oompa.tracking.github               import github_utils
from oompa.tracking.github.GitHub3Helper import GitHub3Helper

from oompa.tracking.TagManager           import TagManager
from oompa.tracking.UpdateLogger         import UpdateLogger

# xxx temp, during a specific problem - all projects claimed to be forked from github3.empty.Empty
import github3


class _Wrapper(dict):

    
    pass


class GitHubTracker:
    """
    support for tracking users, organizations, fork trees, etc.
    """
    
    def __init__(self, config):
        """
        XXX what is config?  (a dictionary?  a real config object?)
        TODO: need a log
        """

        self.config         = config
        self.githubHelper   = GitHub3Helper(config)

        # sometimes we want to turn this off, for testing from-scratch
        self.use_etag = True
        # self.use_etag = False
        # self.use_etag = None

        self._updateLogger  = None
        
        return


    def _getUpdateLogger(self):

        if self._updateLogger is not None:
            return self._updateLogger

        self._updateLogger = UpdateLogger(self.config)
        
        return self._updateLogger

    
    def getGithubURL(self, tail):
        """
        return the 

        tail could be "<entity>" (user or org), or "<entity>/<repo>"
        """
        return "https://github.com/%s" % tail

    
    def getHTMLAnchorText(self, name):

        url  = self.getGithubURL(name)

        return '<a href="%s" target="_blank">%s</a>' % ( url, name )


    def _showEntityTags(self, entityMetadata):
        """report tags and description for the given entity in to the report
        output stream

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
            self.out_stream.write("GitHub entity: %s - %s\n" % (
                entityMetadata.kind, self.getHTMLAnchorText(entityMetadata.name), ))
        else:
            print("GitHub entity: %-25s (%s)" % ( entityMetadata.name, entityMetadata.kind ))

        self._showEntityTags(entityMetadata)
        
        self._showed_entity = True
            
        return
    

    
    def reportListUpdates(self, field, github_obj, entityMetadata, valueAttr):
        """fetch the list named field for the specified github_obj, and
        compare with previous results (reporting new, and no-longer)
        
        github_obj is a User or Organization
        """

        # depending on field, newValue will be a list of Repository or User objects
        #   TODO: how do we check return code
        newValue = self.githubHelper.list(field,
                                          github_obj,
                                          use_etag = self.use_etag)

        # print("reportListUpdates: %s - %s" % ( entityMetadata.name, field, ))
        # print("   new: %r" % newValue)

        if newValue == "no-change":
            # print ("   no change since last check: %s - %s" % ( entityMetadata.name, field, ))
            return
        
        # if not newValue:
        #    print ("   no new value: %s - %s" % ( entityMetadata.name, field, ))
        #    return

        prevValue = entityMetadata.setdefault(field, [])

        #
        # note that a lot of "changes" seem to involve empty values
        #
        # print ("      changed since last check: %s - %s" % ( entityMetadata.name, field, ))
        
        # note: i think that newalue is a list of Repository and
        # prevValue is a list of strings

        if valueAttr is not None:

            # XXX hack - if it's a starred repo, need to access value.repository.attr maybe support introspection?
            if field == "starred_repositories" and valueAttr == "full_name":
                newValue = [ getattr(value.repository, valueAttr) for value in newValue ]
            else:
                newValue = [ getattr(value, valueAttr) for value in newValue ]

            if "" in newValue:
                print("  XXX EntityMetadata.reportListUpdates - empty strings in newValue - %s - %s" % ( field, newValue ))
                print("        not updating local cache")
                # XXX i think that a list of all empties is a sign
                #     that the rpc failed (but didn't fail well)
                #     we should bail out and try again
                # newValue = [ value for value in newValue if value != '' ]
                return

            pass

        # ( addedValues, removedValues )
        #    both are sets

        if "" in prevValue:
            print("  reportListUpdates - empty in prevValue %s (i.e., they were stored in db): %r\n" % ( field, prevValue ))
            # prevValue = [ value for value in prevValue if value != '' ]
            pass
        
        # XXX the lack of writer framework hurts here
        if self._format == "html":
            format_link = self.getHTMLAnchorText
        else:
            format_link = self.getGithubURL

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

            self._getUpdateLogger().logListUpdates(entityMetadata, field, "added",   diffs[0])
            self._getUpdateLogger().logListUpdates(entityMetadata, field, "removed", diffs[1])

            pass
            
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


    def logAllUpdates(self, *args):

        # this one will capture the updates, but not render anything
        xxx


    # ??? did python 2.7 actually break this?
    def discoverHtmlFormat(self, *args, verbose = False):
        """

        TODO: use logging package, vs print to stdout
        """

        # TODO: config
        reportMemberChanges_b = False
        
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

        # XXX temp - should be full html
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

            if verbose:
                print("# %-40s (%s)" % ( entityMetadata.name, entityMetadata.kind ))

                # self.printRatePointsLeft("  rate points before checking entity")

            github_obj  = self.getGithubObject(entityMetadata)

            if github_obj is None:
                print("XXX no github_obj: %s %s" % ( entityMetadata.name, entityMetadata.kind ))
                continue
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

                for repo in newRepos:
                    entityMetadata.append("repoNames", repo.full_name)
                    pass

                # note: this should be the *only* action in recordUpdates,
                #       but helper.printRepos has side-effects of
                #       pulling in extra info about the project (parent and source)
                self._getUpdateLogger().logUpdates(entityMetadata, "repoNames", newRepos)
                pass

            # XXX organizations have followers_count and following_count, but no
            #     followers() or following()

            if github_obj.type == "User":
                self.reportListUpdates("followers",            github_obj, entityMetadata, "login")
                self.reportListUpdates("following",            github_obj, entityMetadata, "login")
                self.reportListUpdates("starred_repositories", github_obj, entityMetadata, "full_name")
                self.reportListUpdates("subscriptions",        github_obj, entityMetadata, "full_name")
            elif github_obj.type == "Organization":

                if reportMemberChanges_b:
                    self.reportListUpdates("public_members", github_obj, entityMetadata, "login")
                    pass
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


    def _discoverListUpdates(self, field, github_obj, entityMetadata, valueAttr):

        # depending on field, newValue will be a list of Repository or User objects
        #   TODO: how do we check return code?
        newValue = self.githubHelper.list(field,
                                          github_obj,
                                          use_etag = self.use_etag)

        if newValue == "no-change":
            # print ("   no change since last check: %s - %s" % ( entityMetadata.name, field, ))
            return
        
        prevValue = entityMetadata.setdefault(field, [])

        #
        # note that a lot of "changes" seem to involve empty values
        #

        # typically, prevValue is list of strings.  extract comparable strings
        # from a list of github things

        if valueAttr is not None:

            # TODO: unroll this, to report which objects have the empty value
            newValue = [ getattr(value, valueAttr) for value in newValue ]

            # note: some objects have/had empty names.  work around that

            if "" in newValue:
                print("  XXX EntityMetadata.reportListUpdates - empty strings in newValue - %s - %s" % ( field, newValue ))
                print("        not updating local cache")
                # XXX i think that a list of all empties is a sign
                #     that the rpc failed (but didn't fail well)
                #     we should bail out and try again
                # newValue = [ value for value in newValue if value != '' ]
                return

            pass

        # ( addedValues, removedValues )
        #    both are sets

        if "" in prevValue:
            print("  reportListUpdates - empty in prevValue %s (i.e., they were stored in db): %r\n" % ( field, prevValue ))
            # prevValue = [ value for value in prevValue if value != '' ]
            pass

        diffs = entityMetadata.getListDiffs(newValue,
                                            prevValue)

        if diffs[0] or diffs[1]:

            for added in diffs[0]:
                self._getUpdateLogger().logListUpdates(entityMetadata, field, "added",   added)
                pass
            
            for removed in diffs[1]:
                self._getUpdateLogger().logListUpdates(entityMetadata, field, "removed", removed)
                pass
            pass
            
        entityMetadata.updateList(field, newValue)

        return

    
    def _discoverUpdates(self, *args):
        """
        baby step toward separating update-harvesting from reporting
        """

        updateLogger = self._getUpdateLogger()
        helper       = self.githubHelper

        # temp, while this is still just a test
        helper._etags._updateEtags = False

        update_metadata = True
        # update_metadata = False

        for entityMetadata in helper.getEntityMetadatas(*args, mustExist = False):
            
            print("# %-40s (%s)" % ( entityMetadata.name, entityMetadata.kind ))

            # repos is a special kind of list - has an api, vs just a field to query
            # TODO: switch to generic listing.  (is that possible?)
            # TODO: we should also record "gone" repos

            github_obj  = self.getGithubObject(entityMetadata)
            # repos       = helper.getRepos(github_obj, sort = "time-newest-first")
            repos       = helper.getRepos(github_obj)

            # TODO: support for filtering *anything* through already-known
            knownRepos  = entityMetadata.setdefault("repoNames", [])
            newRepos    = [ repo for repo in repos if repo.full_name not in knownRepos ]

            if newRepos:

                for repo in newRepos:

                    # actually update, so that we don't re-alert
                    entityMetadata.append("repoNames", repo.full_name)

                    # need to do this to pull in proper "pedigree" (forked from, (parent, source) ...)
                    # XXX we don't have a good place to put that data right now
                    repo.refresh()

                    extra_d = {}

                    extra_d["full_name"] = repo.full_name

                    if repo.parent is not None:
                        extra_d["parent"] = repo.parent.full_name
                        if repo.source != repo.parent:
                            extra_d["source"] = repo.source.full_name
                            pass
                        pass
                    
                    updateLogger.logListUpdate(entityMetadata,
                                               "repoNames",
                                               "added",
                                               **extra_d)
                    pass
                pass

            # XXX organizations have followers_count and following_count, but no
            #     followers() or following()

            if github_obj.type == "User":
                self._discoverListUpdates("followers",            github_obj, entityMetadata, "login")
                self._discoverListUpdates("following",            github_obj, entityMetadata, "login")
                self._discoverListUpdates("starred_repositories", github_obj, entityMetadata, "full_name")
                self._discoverListUpdates("subscriptions",        github_obj, entityMetadata, "full_name")
            elif github_obj.type == "Organization":
                self._discoverListUpdates("public_members", github_obj, entityMetadata, "login")

                # are these not part of organization?
                # self._discoverListUpdates("followers",            github_obj, entityMetadata, "login")
                # self._discoverListUpdates("following",            github_obj, entityMetadata, "login")
                # self._discoverListUpdates("starred_repositories", github_obj, entityMetadata, "full_name")
                # self._discoverListUpdates("subscriptions",        github_obj, entityMetadata, "full_name")
                pass

            if update_metadata:
                entityMetadata.flush()
                pass
            pass
        
        self.githubHelper._etags._updateEtags = True

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


    def reportUpdateHTML(self, *args, start_date = None, end_date = None):
        """
        generate html discovery report over some date range from update logs
        """

        from oompa.tracking.github.EntityMetadata import EntityMetadata

        # XXX cheating
        self._format = format

        # TODO: config
        reportMemberChanges_b = False
        
        self._tag_mgr = TagManager(self.config,
                                   tags_filename = "entity-tags.tsv")

        updateLogger = self._getUpdateLogger()
        helper       = self.githubHelper

        # TODO: use real dateteimes (assuming strings)
        if start_date == end_date:
            date_range_str = start_date
        else:
            date_range_str = "%s-%s" % ( start_date, end_date )
            
        # XXX allow caller to override defaults
        dest_folder    = os.path.join(os.environ["HOME"], "oompa", "discover")
        out_path       = os.path.join(dest_folder, "%s.discover.html" % date_range_str)

        if not os.path.exists(dest_folder):
            os.mkdir(dest_folder)

        print("writing to: %s" % out_path)

        # format_link = helper.getGithubURL
        format_link = self.getHTMLAnchorText
        
        self.out_stream = open(out_path, "w", encoding = 'utf8')

        out_stream = self.out_stream
        
        out_stream.write('<!DOCTYPE html>\n')
        out_stream.write('<meta charset="utf-8">\n')
        out_stream.write('<html>\n')
        out_stream.write('<head>\n')
        out_stream.write('<title>Tracker Discover Report - %s</title>\n' % ( date_range_str, ))
        out_stream.write('</head>\n')
        out_stream.write('<body>\n')

        # XXX temp
        out_stream.write('<pre>\n')
        
        # TODO: if args, pass in a filter
        updates      = updateLogger.getUpdates(start_date = start_date,
                                               end_date   = end_date)
        by_entity    = updateLogger.organizeUpdatesByEntity(updates)

        for entity_info in sorted(by_entity.keys()):

            kind, name     = entity_info
            entityMetadata = EntityMetadata(kind, name, None)

            # print("# %-40s (%s)" % ( entityMetadata.name, entityMetadata.kind ))
            self.out_stream.write("%s - %s\n" % (  entityMetadata.kind, self.getHTMLAnchorText(entityMetadata.name), ))
            self._showEntityTags(entityMetadata)

            updates_for_entity  = by_entity[entity_info]

            # i'm not sure if i need kind and field, or just field
            by_field = updateLogger.organizeUpdatesByField(updates_for_entity)
            fields   = sorted(by_field.keys())

            for field in fields:
                
                out_stream.write("  %s\n" % field)
                out_stream.write("\n")

                updates_for_field = by_field[field]
                
                if field == "repoNames":

                    for update in updates_for_field:

                        repo_url = format_link(update["full_name"])

                        out_stream.write("    repo: %s\n" % repo_url)

                        if update.get("parent"):
                            
                            out_stream.write("      forked: %s\n" % format_link(update["parent"]))
                            
                            if update.get("source") != update.get("parent"):
                                out_stream.write("      source: %s\n" % format_link(update["source"]))
                                pass
                            pass
                        out_stream.write("\n")
                        
                        # TODO: README
                        
                        pass
                    pass
                else:

                    for update in updates_for_field:
                        out_stream.write("    %-8s  %s\n" % ( update["action"], format_link(update["full_name"]) ))
                        pass
                    out_stream.write("\n")
                    pass
                pass
            out_stream.write("\n")
            pass

        out_stream.write('</pre>\n')
        out_stream.write('</body>\n')
        out_stream.write('</html>\n')

        if out_stream != sys.stdout:
            out_stream.close()
            pass

        return


    

    def removeEntities(self, entities):
        """entities is list of entity specs - user/...,
        org[anization]/..., or un-qualified entity name

        """

        return self.githubHelper.removeEntities(entities)


    def close(self):

        self.githubHelper.close()
        
        if self._updateLogger is not None:
            self._updateLogger.close()

        return
    
    pass
