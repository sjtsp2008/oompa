#
# FileMetadataStore.py
#

"""
package oompa.tracking.github
"""

import json
import os

from oompa.tracking.github.GitHubMetadataStore  import GitHubMetadataStore
from oompa.tracking.github.EntityMetadata       import EntityMetadata


class FileMetadataStore(GitHubMetadataStore):
    """
    filesystem-based GitHubMetadataStore

    """


    def __init__(self, config, githubHelper):

        GitHubMetadataStore.__init__(self, config, githubHelper)
        
        # XXX get everything from config
        self.root = config.get("github.meta.fs.root")

        if self.root is None:
            self.root = os.path.join(os.environ["HOME"], "github_meta_cache")
            pass
        
        return
    

    def _getFolder(self, kind, name):

        return os.path.join(self.root, kind.lower(), name)

    
    def findEntityFolder(self, name):

        for kind in self._kinds:
            folder = self._getFolder(kind, name)
            if os.path.exists(folder):
                return folder
            pass

        return None
        
    def createFolder(self, kind, name):

        folder = self._getFolder(kind, name)

        if os.path.exists(folder):
            return

        os.mkdir(folder)

        return folder
        
    
    def _getMetadataPath(self, entityMetadata):

        folder = self._getFolder(entityMetadata.kind, entityMetadata.name)
        
        return os.path.join(folder, "tracker.meta.json")


    
    def _loadEntityMetadata(self, entityMetadata):

        metadataPath = self._getMetadataPath(entityMetadata)
        
        # print("_loadEntityMetadata: %s - %s - %s" % ( entityMetadata.kind, entityMetadata.name, metadataPath ))
        
        if os.path.exists(metadataPath):
            # print("  loading: %s" % metadataPath)
            return json.load(open(metadataPath))

        return {}

    
    def saveEntityMetadata(self, entityMetadata):

        metadataPath = self._getMetadataPath(entityMetadata)

        # print("FileMetadataStore.saveEntityMetadata: %s" % metadataPath)

        folder       = os.path.dirname(metadataPath)
        
        if not os.path.exists(folder):
            # TODO: the parent still might not exist
            os.mkdir(folder)
            pass

        # XXX cheating
        meta = entityMetadata._meta
        
        file = open(metadataPath, "w")
        json.dump(meta, file)
        file.close()

        return


    def setMetadata(self, folder, key, value):

        xxx

        return

    
    def getNamesAndFolders(self, *names, mustExist = True):
        """

        currently may yield None as folder.
        XXX does not currently implement createFolders

        
        """
        
        if not names:

            # iterate over all

            for kind in self._kinds_lowered:

                kind_root = os.path.join(self.root, kind)
                
                for filename in os.listdir(kind_root):
                    childPath = os.path.join(kind_root, filename)
                    if os.path.isdir(childPath):
                        yield os.path.basename(childPath), childPath
                        pass
                    pass
                pass
                    
            return
        
        for name in names:

            folder = self.findEntityFolder(name)

            if folder is None and mustExist:
                xxx
                pass

            github_obj = self.githubHelper.getGithubObject(name)

            # note that failures don't return None, they return a NullObject
            if github_obj:
                # print("    github_obj: %s - %r" % ( github_obj.type, github_obj ))
                folder = self.createFolder(github_obj.type, name)
                # print("  created folder: %s" % folder)
                pass
            
            yield name, folder
            pass

        return


    def getEntityMetadata(self, kind, name):
        """
        instantiate an EntityMetadata for the specified kind and name
        """
        
        kind_root = os.path.join(self.root, kind)
        childPath = os.path.join(kind_root, name)

        entityMetadata               = EntityMetadata(kind, name, self)
        entityMetadata._githubHelper = self._githubHelper

        if os.path.isdir(childPath):
            entityMetadata._meta = self._loadEntityMetadata(entityMetadata)
            pass
        
        return entityMetadata

    
    
    def getEntityMetadatas(self, *names, mustExist = True):
        """generate stream of EntityMetadata
        
        createFolders is used as a flag to be able to not return a
        metadata if the entity has not been discovered before

        TODO: factor as much as possible in to parent class

        """

        if not names:

            # iterate over all

            for kind in self._kinds_lowered:

                kind_root = os.path.join(self.root, kind)
                
                for filename in os.listdir(kind_root):

                    entityMetadata = self.getEntityMetadata(kind, filename)

                    if entityMetadata is not None:
                        yield entityMetadata
                        pass
                    pass
                pass
                    
            return
        
        for name in names:

            folder = self.findEntityFolder(name)

            if folder is None and mustExist:
                xxx
                pass
            
            # note: 

            github_obj = self._githubHelper.getGithubObject(name)

            # note that failures don't return None, they return a NullObject
            if github_obj:
                # print("    github_obj: %s - %r" % ( github_obj.type, github_obj ))
                folder = self.createFolder(github_obj.type, name)
                # print("  created folder: %s" % folder)
                pass

            print("GO: %r" % github_obj)
            
            # TODO: should not lower - just use their type
            kind = github_obj.type.lower()
            
            entityMetadata = EntityMetadata(kind, name, self)
            
            # yield name, folder
            yield entityMetadata
            pass

        return
    
    pass

