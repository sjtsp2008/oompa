#
#
#


class EntityMetadataWrapper:

    def __init__(self, entity, entityMetadata, githubHelper):

        self.entity         = entity
        self.entityMetadata = entityMetadata
        self.githubHelper   = githubHelper
        
        return

    def useCachedOrGetList(self, slot, use_etag = False):
        """
        """

        print("useCachedOrGetList(): %s" % slot)
        
        # TODO: check age
        value = self.entityMetadata.get(slot)

        if value:
            print("  value cached")
            return value

        print("need to get value")

        value = list(self.githubHelper.list(slot, self.entity, use_etag))

        print("  value: %s" % value)

        xxx
        
        # TODO: stuff the value in metadata (possibly update and return merged

        return value
    
    pass
