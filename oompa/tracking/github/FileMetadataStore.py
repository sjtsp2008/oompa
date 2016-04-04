#
# FileMetadataStore.py
#

"""
package oompa.tracking.github
"""

import json
import os
import shutil

from oompa.tracking.github.GitHubMetadataStore  import GitHubMetadataStore
from oompa.tracking.github.EntityMetadata       import EntityMetadata

from oompa.tracking.github                      import github_utils



class FileMetadataStore(GitHubMetadataStore):
    """
    filesystem-based GitHubMetadataStore

      github_meta_cache/user/<username>/tracker.meta.json

    (i think i was expecting more files per entity.  could simplify)

    """

    def __init__(self, config, githubHelper):

        GitHubMetadataStore.__init__(self, config, githubHelper)
        
        # XXX get everything from config
        self.root = config.get("github.meta.fs.root")

        if self.root is None:
            self.root = os.path.join(os.environ["HOME"], "oompa", "github_meta_cache")
            pass
        
        return
    

    def _getFolder(self, kind, name = None):

        folder = os.path.join(self.root, kind.lower())

        if name is not None:
            folder = os.path.join(folder, name)

        return folder

    
    def findEntityFolder(self, name, kind = None):
        """

        """

        xxx
        
        if kind is not None:
            folder = self._getFolder(kind, name)
            if os.path.exists(folder):
                return folder
            return None
                              
        for kind in self._kinds:
            folder = self._getFolder(kind, name)
            if os.path.exists(folder):
                return folder
            pass

        return None

    def createFolder(self, kind, name = None):

        # smoke out old-style
        if name:
            xxx
        
        folder = self._getFolder(kind, name)

        if os.path.exists(folder):
            return

        os.mkdir(folder)

        return folder

    
    def _getMetadataPath(self, entityMetadata):

        folder = self._getFolder(entityMetadata.kind)
        path   = os.path.join(folder, "%s.tracker.meta.json" % entityMetadata.name)
        
        return path

    
    
    def _loadEntityMetadata(self, entityMetadata):

        metadataPath = self._getMetadataPath(entityMetadata)
        
        # print("_loadEntityMetadata: %s - %s - %s" % ( entityMetadata.kind, entityMetadata.name, metadataPath ))
        
        if os.path.exists(metadataPath):
            # print("FileMetadataStore._loadEntityMetadata - loading meta: %s" % metadataPath)
            entityMetadata._meta = json.load(open(metadataPath))
                                 
        return

    
    def saveEntityMetadata(self, entityMetadata):

        metadataPath = self._getMetadataPath(entityMetadata)

        print("FileMetadataStore.saveEntityMetadata: %s - %s" % ( entityMetadata.name, metadataPath ))

        folder       = os.path.dirname(metadataPath)
        
        if not os.path.exists(folder):
            # TODO: the parent still might not exist
            os.mkdir(folder)
            pass

        # XXX cheating
        meta = entityMetadata._meta

        # print("META:")
        # print(json.dumps(meta, indent = 2))
        
        file = open(metadataPath, "w")
        # json.dump(meta, file)
        json.dump(meta, file, indent = 2)
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

        xxx
        
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

    
    def getEntityMetadatas(self, *names, mustExist = True):
        """generate stream of EntityMetadata

        if names specified, (possibly create and) generate metadatas
        for those things.  if names is not specified, generate
        metadatas for everything in the metadata store (i.e., has been
        tracked previously).
        
        createFolders is used as a flag to be able to not return a
        metadata if the entity has not been discovered before

        TODO: factor as much as possible in to parent class

        """

        if not names:

            # TODO: should be using an enumeration helper
            
            # iterate over all registered entities

            for kind in self._kinds_lowered:

                kind_root = os.path.join(self.root, kind)

                for filename in os.listdir(kind_root):
                    name           = filename.split(".")[0]
                    entityMetadata = self.getEntityMetadata(kind, name)

                    if entityMetadata is not None:
                        yield entityMetadata
                        pass
                    pass
                pass
                    
            return

        for kind, name in github_utils.getKindAndName(names):

            github_obj = self._githubHelper.getGithubObject(name, kind = kind)

            # note that failures don't return None, they return a NullObject
            if github_obj:
                folder = self.createFolder(github_obj.type)
                pass

            # TODO: should not lower - just use their type
            kind           = github_obj.type.lower()
            
            entityMetadata = EntityMetadata(kind, name, self)
            metadataPath   = self._getMetadataPath(entityMetadata)

            if mustExist and not os.path.exists(metadataPath):
                xxx
                pass

            self._loadEntityMetadata(entityMetadata)
            
            # yield name, folder
            yield entityMetadata
            pass

        return


    
    def removeEntities(self, *entitySpecs):
        """
        delete entities from local tracking db
        """

        # 20160328 - add poison until reorg to new scheme is complete
        xxx
        
        for entitySpec in entitySpecs:

            kindsNames = github_utils.getKindAndName([ entitySpec, ])
            kindsNames = list(kindsNames)
            kind, name = kindsNames[0]

            if kind is None:
                # try both kinds.  but there can only be one of the two
                xxx
                pass
            
            folder = self.findEntityFolder(name, kind = kind)

            if folder is None:
                print("XXX entity not tracked: %s (kind: %s)" % ( entitySpec, kind ))
                continue

            print("# removing folder: %s" % folder)

            shutil.rmtree(folder)
            pass
            
        return


    def updateStorageScheme(self):

        print("  root: %s" % self.root)

        for kind in self._kinds_lowered:

            kind_root = os.path.join(self.root, kind)

            print("    kind_root: %s" % kind_root)
            
            for child in os.listdir(kind_root):

                if child.endswith(".json"):
                    continue

                metadataPath = os.path.join(kind_root, child, "tracker.meta.json")
                newPath      = os.path.join(kind_root, "%s.tracker.meta.json" % child)

                print("      meta: %s" % metadataPath)
                print("      new:  %s" % newPath)

                if not os.path.exists(metadataPath):
                    print("  must have already moved file")
                    continue
                
                os.rename(metadataPath, newPath)
                shutil.rmtree(os.path.dirname(metadataPath))
                
                # print("breaking after one - 1"); break

            # print("breaking after one - 2"); break
            
        return

    
    pass

