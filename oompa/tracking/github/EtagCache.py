#
#
#

import json
import os


class EtagCache:
    """
    TODO: do this with personal sqlite3, or couch, or mongo, or something
    """
    
    def __init__(self, path):

        self.path  = path

        #
        # { thing_id -> { qualifier -> etag } }
        #
        self.etags_d = self._load()

        return


    def _load(self):

        if os.path.exists(self.path):
            return json.load(open(self.path))
        
        return {}


    def _save(self):

        file = open(self.path, "w")
        json.dump(self.etags_d, file, indent = 2)
        file.close()

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

        if self.get(thing, qualifier) == etag:
            return

        key     = self._getKey(thing)
        for_key = self.etags_d.setdefault(key, {})

        for_key[qualifier] = etag

        # TODO: set dirty marker, just flush at end
        self._save()
        
        return

    pass
