#
#
#


class EntityMetadata:
    """represents a *partial* view of github metadata - only what has
    been requested so far

    TODO: i think you have to make some sort of extra webservice call to get the
          accurate forked-from state of a repo

    """
    
    def __init__(self, kind, name, backingStore):

        # print("EntityMetadata(): %s - %r" % ( kind, name ))
        
        self.kind         = kind
        self.name         = name
        self.backingStore = backingStore

        self._meta          = {}
        
        # TODO: change to be a dictionary of what has to be flushed
        self._meta_changed  = False
        
        return


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
            print("XXX removing empties from previous value: %s - %s" % ( field, newValue ))
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



    

    def diffLists(self, field, newValue, prevValue, valueAttr = None):
        """
        
        TODO: there's not a good reason that thisis a method on EntityMetadata
        """
        
        # print("diffLists: %s - %s" % ( thingName, field ))
        # print("  new full value:")

        if valueAttr is not None:
            newValue = [ getattr(value, valueAttr) for value in newValue ]
            pass

        # i think that if this happens, we should have waited, checked iterator
        # status code, and tried the call again
        if "" in newValue:
            print("  diffLists - at least one empty in newValue: %s" % newValue)
            pass
        
        for value in newValue:

            marker = ""

            if value in prevValue:
                marker = "(already on list)"
                continue
                # pass

            # XXX want a general field-specific hook for transforming value
            # XXX don't assume http://github.com
            #
            # the most common thing i do from discover output is crawl around github.
            # having to paste a suffix in is a pain
            #
            if field == "starred_repositories":
                value = "http://github.com/%s" % value
                pass
                
            print("  new: %-20s  %-50s %s" % ( field, value, marker ))
            pass
        
        # if prevValue is None:
        #    print("    previous list empty")
        #    return

        # XXX trying to isolate a problem - i think when we get an incomplete positive response
        if "" in prevValue:
            print("  diffList - empty in prevValue: %r" % prevValue)
            pass
        
        for value in prevValue:
            if value not in newValue:
                print("  not on list any more: %s: %r" % ( field, value ))
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

