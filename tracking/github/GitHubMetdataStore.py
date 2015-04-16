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



def getGitHubMetadataStore(config):
    """
    factory for specific backends
    """

    from oompa.tracking.github.FileMetadataStore import FileMetadataStore
    
    # XXX support other backends - esp sqlite
    
    metadataStore = FileMetadataStore(config, self)
    
    return metadataStore
