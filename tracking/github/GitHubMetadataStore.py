#
# GitHubMetadataStore.py
#

"""
package oompa.tracking.github
"""


class GitHubMetadataStore:

    _kinds         = [ "User", "Organization", "Repository" ]
    _kinds_lowered = [ kind.lower() for kind in _kinds ]


    
    def __init__(self, config, githubHelper):

        self._config       = config

        self._githubHelper = githubHelper
        
        return


    def getEntityMetadata(self, folder):
        """
        returns EntityMetadata
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
