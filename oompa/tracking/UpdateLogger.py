#
# UpdateLogger.py
#

"""
package oompa.tracking

TODO: stil waffling about whether to log two-columns - "datetime {json}" or "{json-with-datetime-field}"

"""

import json
import os

from datetime import datetime



class UpdateLogger:
    """
    records updates for later replay
    """
    
    def __init__(self, config):

        self.config = config

        # XXX really get from config
        config_base  = os.environ["HOME"]
        oompa_base   = os.path.join(config_base, "oompa")

        self._updates_folder = os.path.join(oompa_base, "updates")

        # cache
        self._streams = {}
        
        return

    # ###
    #
    # file-based subclass
    # TODO: factor out to a subclass
    #


    def _getUpdatePath(self, datetime = None):

        if isinstance(datetime, str):
            yyyymmdd = datetime
        else:
            # in file subclass, we assume datetime is not none
            yyyymmdd = datetime.strftime("%Y%m%d")
            
        return os.path.join(self._updates_folder, "%s.updates.log" % yyyymmdd)
        
    
    def _getUpdateStream(self, datetime = None):

        path = self._getUpdatePath(datetime)
            
        if path not in self._streams:
            self._streams[path] = open(path, "a")
            
        # assumes that oompa_base exists
        if not os.path.exists(self._updates_folder):
            os.mkdir(self._updates_folder)
            
        return self._streams[path]
    

    def _logUpdate(self, info_d):

        now                = datetime.now()
        info_d["datetime"] = now.strftime("%Y%m%d-%H:%M:%S")
        updateStream       = self._getUpdateStream(now)

        updateStream.write("%s\n" % json.dumps(info_d))

        # print("#   wrote update: %s" % json.dumps(info_d))
        # updateStream.flush()
        
        return

    #
    # ###


    def logListUpdate(self, entityMetadata, fieldName, action, **extra):

        # i think this may end up being the only kind of update
        info_d = {
            "kind":         "list3",
            "subject_kind": entityMetadata.kind,
            "subject":      entityMetadata.name,
            "field":        fieldName,
            "action":       action,
        }

        info_d.update(extra)

        self._logUpdate(info_d)        

        return
        

        
    def logUpdates(self, entityMetadata, fieldName, newItems):
        """
        
        XXX i don't think this is generic across any kind of update
        """

        if not newItems:
            return
        
        info_d = {
            "kind":         "list1",       # stupid - merge list1 and list2 handling
            "field":        fieldName,
            "subject_kind": entityMetadata.kind,
            "subject":      entityMetadata.name,
        }

        for item in newItems:

            # XXX non-generic
            if fieldName == "repoNames":

                # note that created_at and updated_at could be fetched later.  updated will certainly change
                
                info_d["full_name"]  = item.full_name

                # info_d["created_at"] = item.created_at
                # these assume that someone has called refresh
                # info_d["parent"]     = item.parent
                # info_d["source"]     = item.source

                # note: *not* including blurb

            else:
                
                print("  logUpdates() - *not* a repoName: %s" % fieldName)
                pass

            self._logUpdate(info_d)
            pass
        
        return
    
    def logListUpdates(self, entityMetadata, fieldName, action, values):
        """
        
        XXX i don't think this is generic across any kind of update

        TODO: use self.logListUpdate, to get more normalized
        """

        info_d = {
            "kind":         "list2",
            "field":        fieldName,
            "action":       action,
            "subject_kind": entityMetadata.kind,
            "subject":      entityMetadata.name,
        }

        # TODO: probably just write out full list in one record
        for value in values:

            info_d["full_name"]  = value

            # TODO: if action is added, refresh the metadata to add parent and source
            
            # TODO: 
        
            # 
            # info_d["created_at"] = item.created_at
            # these assume that someone has called refresh
            # info_d["parent"]     = repo.parent
            # info_d["source"]     = item.source
            #
            # note: *not* including the blurb - renderer can look it up
            
            self._logUpdate(info_d)
            pass
        
        return

    
    def getUpdates(self, start_date = None, end_date = None):
        """
        generate stream of updates

        TODO: support various filters
        """

        # print("UpdateLogger.getUpdates(): %s - %s" % ( start_date, end_date ))

        # TODO: assuming today is dumb.  maybe discover most recent
        #       update?
        if end_date is None:
            end_date = datetime.now()
            
        if start_date is None:
            start_date = end_date

        if start_date != end_date:
            xxx
            
        # XXX need date_utils.date_range
        date_range = [ start_date, ]
        
        for date in date_range:
            # yyyymmdd    = date.strftime("%Y%m%d")
            yyyymmdd    = date
            update_path = self._getUpdatePath(yyyymmdd)
            if not os.path.exists(update_path):
                print("#  update_path does not exist: %s" % update_path)
                continue

            for line in open(update_path):
                yield json.loads(line)

        return
        

    def organizeUpdatesByEntity(self, updates):
        """
        organize updates by ( subject_kind, subject ) from the update
        """

        byEntity = {}

        for update in updates:
            entity = ( update["subject_kind"], update["subject"] )
            byEntity.setdefault(entity, []).append(update)
            pass
        
        return byEntity


    def organizeUpdatesByKind(self, updates):
        """
        organize updates by ( kind, ) from each update
        """

        by_kind = {}

        for update in updates:
            by_kind.setdefault(update["kind"], []).append(update)
            pass
        
        return by_kind


    def organizeUpdatesByField(self, updates):
        """
        organize updates by ( field, ) from each update
        """

        by_field = {}

        for update in updates:
            by_field.setdefault(update["field"], []).append(update)
            pass
        
        return by_field
    


    
    
    def close(self):

        map(lambda stream: stream.close(), self._streams)
        
        return
                           
    pass
