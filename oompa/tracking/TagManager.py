#
# TagManager.py
#

"""
package oompa.tracking
"""

import os


class TagManager:
    """hack to manage simple tagging system

    tag files are simple multi-space-separated files

      key    tag1,tag2   comment


    assumes that the tag db is "personal" sized, and easily loadable
    in to memory.  any update appends to the file

    the tag files are largely manual-edit right now

    note that different tag spaces are currently managed in different
    files (project-tags, entity-tags)

    XXX currently specific to an oompa Project

    """
    
    def __init__(self, config, tags_filename = None):

        # TODO: unify the tags db.
        # TODO: use a real delicious-style db
        if tags_filename is None:
            tags_filename    = "project-tags.tsv"
            pass
                
        # XXX use config to set up home of tags db.
        #     it's not currently used

        # XXX what is current best practice for stashing metadata?
        home             = os.environ["HOME"]
        # self._tags_path  = os.path.join(home, ".oompa", tags_filename)
        self._tags_path  = os.path.join(home, "oompa", "tags", tags_filename)

        self._tags_db        = None

        return

    
    def _loadTags(self):
        """
        replace current in-memory tags with contents of file
        """

        # reset
        self._tags_db = {}

        if not os.path.exists(self._tags_path):
            return

        # note: for easy manual editing, using at least two spaces as the separator.
        #       probably makes it a pain for csv library

        line_num = 0
        
        for line in open(self._tags_path):

            line_num += 1
            
            line = line.strip()
            if not line or line[0] == "#":
                continue

            # XXX legacy
            if "\t" in line:
                xxx
                line = line.replace("\t", "  ")
                pass
            
            pieces      = [ piece.strip() for piece in line.split("  ") if piece != "" ]

            repo_url    = pieces[0]

            # support incomplete lines - place-holder for what i need to backfill
            if len(pieces) > 1:
                tags        = pieces[1].split(",")
                description = "  ".join(pieces[2:])
            else:
                tags_csv    = ""
                description = ""
                pass
            
            self._tags_db[repo_url] = ( tags, description )
            pass
        
        return


    def _saveTags(self):

        # XXX implement me - save the complete file
        
        return
    

    def _getTagsDB(self):

        if self._tags_db is None:
            self._loadTags()
            pass

        return self._tags_db

    
    def getTags(self, key):
        """
        returns ( [ tag, ... ], description ) or None

        """
        
        return self._getTagsDB().get(key)
        
    
    def getTagInfo(self, project):
        """
        XXX the TagManager should probably not need to be aware of Project
        """
        return self.getTags(project.getSourceURL())

    
    def getTagInfos(self, *patterns):
        
        for project in self.getProjects(self.tracking_folder, *patterns):

            source_url = project.getSourceURL()
            tagInfo    = self.getTags(source_url)

            yield project, tagInfo
            pass

        return
        

    def setTagInfo(self, key, tags, description):

        # TODO:
        #   - make a backup of previous
        #     - but only N backups at most
        #   - check if it's already in db
        #   - write out tag db, in a predictable way - *append*
        # 
        
        print("# TagManager.setTagInfo():")
        print("# %s   %s   %s" % ( key, ",".join(tags), description ))

        print("# just appending to bottom of tags file right now")

        
        out_stream = open(self._tags_path, "a")

        out_stream.write("\n")
        out_stream.write("%s   %s   %s\n" % ( key, ",".join(tags), description ))
        out_stream.write("\n")

        out_stream.close()
        
        return
    
    pass
