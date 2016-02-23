#
# EntityMetadata.py
#

"""
package tracking
"""

# XXX should not be visible here.  very special-purpose
# import webbrowser

# XXX just in support of html/report hack
import sys


class EntityMetadata:
    """represents a *partial* view of github metadata - only what has
    been requested so far

    TODO: i think you have to make some sort of extra webservice call to get the
          accurate forked-from state of a repo

    """
    
    def __init__(self, kind, name, backingStore):
        """
        backingStore is probably a GitHubMetadataStore
        """
        
        # print("EntityMetadata(): %s - %r" % ( kind, name ))
        
        self.kind         = kind
        self.name         = name
        self.backingStore = backingStore

        # TODO: should be get_boolean()
        self._open_tabs_in_browser_b  = backingStore._config.get("oompa.discover.open-new-projects-in-browser", False)
        self._max_new_tabs_per_entity = 8
        
        self._meta          = {}
        
        # TODO: change to be a dictionary of what has to be flushed
        self._meta_changed  = False
        
        return


    def getGithubURL(self, prefix = None):
        """
        prefix is http or https.  defaults to http
        """
        if prefix is None:
            prefix = "http"
            pass
        
        return "%s://github.com/%s" % ( prefix, self.name )

    
    def setdefault(self, slot, defaultValue):
        """
        XXX this does not make sense
        """
        
        return self._meta.setdefault(slot, defaultValue)


    def get(self, slot):

        return self._meta.get(slot)
    
    
    def append(self, slot, value):

        self._meta[slot].append(value)

        self._meta_changed = True

        return


    
    def updateList(self, field, newValue, valueAttr = None):
        """

        mix 
        """
        
        # XXX still trying to understand if we get "full" updates whenever any new
        #     item is added to list

        prevValue = self.setdefault(field, [])

        if valueAttr is not None:
            newValue = [ getattr(value, valueAttr) for value in newValue ]
            pass

        #
        # 20150403 - trying to isolate where empty values are coming from (and whether
        #            they are an indication of not getting complete results from webservice)
        #
        if "" in prevValue:
            print("XXX removing empties from previous value: %s - %s" % ( field, prevValue ))
            prevValue = [ value for value in prevValue if value != "" ]
            pass

        if "" in newValue:
            print("XXX mixing a new empty value in to list: %s - %s - %s" % ( field, valueAttr, newValue ))
            pass

        for value in newValue:
            # print("  updateList: %s - %s" % ( field, value ))
            if value not in prevValue:
                prevValue.append(value)
                self._meta_changed = True
                pass
            pass

        for value in prevValue:
            if value not in newValue:
                prevValue.remove(value)
                self._meta_changed = True
                pass
            pass
        
        return


    def getListDiffs(self,
                     newValues,
                     prevValues):
        """

        TODO: refactor to a helper - there's not a good reason that this is a method on EntityMetadata


        """

        newSet  = set(newValues)
        prevSet = set(prevValues)

        return newSet - prevSet, prevSet - newSet
        
    

    
    def diffLists(self,
                  field,
                  newValue,
                  prevValue,
                  out_stream  = None,
                  format_link = None):
        """

        TODO: should accept the list generated by getListDiffs

        TODO: refactor to a helper - there's not a good reason that this is a method on EntityMetadata

        XXX format_link is not really optional any more.  assumed to at least be identity
        

        """

        
        # print("diffLists: %s - %s" % ( thingName, field ))
        # print("  new full value:")

        if out_stream is None:
            out_stream = sys.stdout
            pass
        
        # if valueAttr is not None:
        #    newValue = [ getattr(value, valueAttr) for value in newValue ]
        #    pass
        # 
        # # i think that if this happens, we should have waited, checked iterator
        # # status code, and tried the call again
        # if "" in newValue:
        #    out_stream.write("  diffLists - at least one empty in newValue: %s\n" % newValue)
        #    pass

        for value in newValue:

            marker = ""

            if value in prevValue:
                # marker = "(already on list)"
                continue

            # XXX want a general field-specific hook for transforming value
            # XXX don't assume http://github.com
            #
            # the most common thing i do from discover output is crawl around github.
            # having to paste a suffix in is a pain
            #
            if field == "starred_repositories":
                value = format_link(value)

            if marker:
                out_stream.write("  new: %-20s  %-50s %s\n" % ( field, value, marker ))
            else:
                out_stream.write("  new: %-20s  %s\n" % ( field, value, ))

        # XXX trying to isolate a problem - i think when we get an incomplete positive response
        #     sometimes.  should be fixed
        # if "" in prevValue:
        #    out_stream.write("  diffLists - empty in prevValue (i.e., they were stored in db): %r\n" % prevValue)
        #    prevValue = [ value for value in prevValue if value != '' ]
        #    pass
        
        for value in prevValue:
            if value not in newValue:
                out_stream.write("  not on list any more: %s: %r\n" % ( field, value ))
                pass
            pass

        return
    
    def flush(self):

        if self._meta_changed:
            self.backingStore.saveEntityMetadata(self)
            pass

        return
    
    # TODO: on __del__, flush any changes
    
    pass

