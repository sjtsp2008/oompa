#
# EtagCache.py
#

"""
package oompa.tracking.github
"""

import json
import os


class EtagCache:
    """manage github etags, which are used to cache results locall -
    request only changes since some snapshot

    tags are per thing per feature (e.g. 

    TODO: do this with personal sqlite3, or couch, or mongo, or something

    """
    
    def __init__(self, path):

        self.path  = path

        #
        # { thing_id -> { qualifier -> etag } }
        #
        self.etags_d = self._load()

        self._dirty = False

        # mostly used during testing
        self._updateEtags = True
        
        return


    def _load(self):

        if os.path.exists(self.path):
            return json.load(open(self.path))
        
        return {}


    def _save(self):

        if self._dirty:
            stream = open(self.path, "w")
            json.dump(self.etags_d, stream)
            stream.close()
            self._dirty = False
            
        return
    

    def _getKey(self, thing):

        return "%s/%s" % ( thing.type, thing.login )        

    
    def get(self, thing, qualifier):

        # print("  EtagCache.get(): %s %s" % ( thing, qualifier ))

        # we immediately create the qualifier dict, assuming that the qualifier
        # will be set soon
        
        key     = self._getKey(thing)
        for_key = self.etags_d.setdefault(key, {})

        # print("    for_key: %s - %s" % ( key, for_key ))
        
        return for_key.get(qualifier)
    

    def set(self, thing, qualifier, etag):

        # print("  EtagCache.set(): %s %s %s" % ( thing, qualifier, etag ))

        if not self._updateEtags:
            return
        
        if self.get(thing, qualifier) == etag:
            return

        key     = self._getKey(thing)
        for_key = self.etags_d.setdefault(key, {})

        for_key[qualifier] = etag

        self._dirty = True
        
        return

    
    def close(self):

        self._save()

        return

    
    pass
