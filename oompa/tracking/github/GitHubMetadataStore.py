#
# GitHubMetadataStore.py
#

"""
package oompa.tracking.github
"""


class GitHubMetadataStore:
    """base class for snapshotting metadata about github objects (users,
    organizations, repositores), mostly in support of watching changes
    over time

    """
    
    _kinds         = [ "User", "Organization", "Repository" ]
    _kinds_lowered = [ kind.lower() for kind in _kinds ]
    
    def __init__(self, config, githubHelper):
        """
        config is a what?
        """
        
        self._config       = config

        self._githubHelper = githubHelper
        
        return


    def getEntityMetadata(self, folder):
        """
        returns EntityMetadata
        """

        raise NotImplementedError


    def getEntityMetadatas(self, *names, mustExist = True):
        """generate stream of EntityMetadata

        if names specified, (possibly create and) generate metadatas
        for those things.  if names is not specified, generate
        metadatas for everything in the metadata store (i.e., has been
        tracked previously).
        
        createFolders is used as a flag to be able to not return a
        metadata if the entity has not been discovered before
        """

        raise NotImplementedError
    

    def removeEntities(self, *entitySpecs):
        """
        delete entities from local tracking db
        """

        raise NotImplementedError
    
    # get

    # set
    
    pass



def getGitHubMetadataStore(config, helper):
    """
    factory for specific backends
    """


    storeType = config.get("github.meta.store", "file")

    # TODO: use a plugin registry
    if storeType == "file":
        from oompa.tracking.github.FileMetadataStore import FileMetadataStore
        storeClass = FileMetadataStore
    elif storeType == "sqlite":
        from oompa.tracking.github.SQLiteGitHubMetadataStore import SQLiteGitHubMetadataStore
        storeClass = SQLiteMetadataStore
    elif storeType == "neo4j":
        from oompa.tracking.github.Neo4jGitHubMetadataStore import Neo4jGitHubMetadataStore
        storeClass = Neo4jGitHubMetadataStore
    else:
        xxx
        pass

    metadataStore = storeClass(config, helper)
    
    return metadataStore
