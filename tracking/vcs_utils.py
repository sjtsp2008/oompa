#
# vcs_utils.py
#

"""

tools for working with various version control systems,
both local and remote

"""

import os
import re

from pylib.util import file_utils


#
# local clues - if these folders exist in a folder,
# it is a certain flavorr of vcs
#
# XXX discover from plugins, or get from config
# 
# _vcs_types  = [ 'hg', 'bzr', 'svn', 'git', 'cvs' ]

_vcs_clues  = [ 
    ( 'hg',   '.hg' ),
    'bzr', 
    ( 'svn', '.svn' ),
    ( 'git', ".git" ),

    # ( 'cvs', '.cvs' ),
    ( 'cvs', 'CVS' ),
    ]


def determine_vcs_type(project_path = None,
                       project      = None):
    """

    determine vcs flavor of a local source tree, by peeking for
    particular clues
    
    returns a string

    project is a path
    
    will find either:

      project/hg
      project/.hg
    
    XXX may be two layers down (e.g., in trunk, for svn)
    
    """
    
    if project_path is None:
        project_path = project.path
        pass
    
    for vcs_type_info in _vcs_clues:
        
        if isinstance(vcs_type_info, tuple):
            vcs_type, vcs_support_folder = vcs_type_info
        else:
            vcs_type                     = vcs_type_info
            vcs_support_folder           = None
            pass
        
        # print '  %r  %r' % ( vcs_type, vcs_support_folder )
        
        if os.path.exists(os.path.join(project_path, vcs_type)):
            return vcs_type
        
        if vcs_support_folder and os.path.exists(os.path.join(project_path, 
                                                              vcs_support_folder)):
            return vcs_type
        
        pass
    
    return None


# prioritized - first match wins
# note that the patterns only match the prefix.  does not need to capture the full url
# XXX needs to be in a set of files
_patterns_flavors = [

    ( ".*?svn",      "svn" ),       # contains svn in 

    ( "^git://",                  "git" ),
    ( ".*?\.git$",                "git" ),
    ( ".*?github\.",              "git" ),
    ( "http://git.code.sf.net/",  "git" ),

    ( ".*?hgroot",   "hg"  ),

    # XXX bitbucket supports both hg and git.  i think 
    #     we may need to try twice
    # ( ".*?bitbucket.org", "hg|git" )
    ( ".*?bitbucket.org", "hg" ),

    ( ".*?hg\.",          "hg" ),
    ( ".*?/hg/",          "hg" ),

    # does freshfoo support any other flavors?
    ( ".*?freshfoo.com", "hg" ),

    ]

def detect_vcs_type_from_source(source_spec):
    """
    
    try to determine vcs type from url.

    walks a prioritized list of patterns and 


    source_spec is almost always a url


    """

    # print "vcs_utils.detect_vcs_type_from_source(): %s" % source_spec

    # TODO: need to create a table of patterns to vcs type

    for pattern, flavor in _patterns_flavors:
        if re.match(pattern, source_spec):
            return flavor
        pass

    return None

    xxx

    return None



def find_vcs_folder(project_path = None,
                    project      = None):
    """
    
    in general, assumes a convention: path/{svn,hg,bzr,...}/<checkout>
    
    note that if multiple types of checkout exist, we will pick
    the first
    
    TODO:
    - delegate to determine_vcs_type
    """
    
    if project_path is None:
        project_path = project.path
        pass

    # print "find_vcs_folder: %s" % project_path
    
    for vcs_type_info in _vcs_clues:
        
        if isinstance(vcs_type_info, tuple):
            vcs_type, vcs_support_folder = vcs_type_info
        else:
            vcs_type           = vcs_type_info
            vcs_support_folder = None
            pass
        
        folder = os.path.join(project_path, vcs_type)
        
        if os.path.exists(folder):
            return folder
        
        if vcs_support_folder and os.path.exists(os.path.join(project_path, 
                                                              vcs_support_folder)):
            return project_path
        pass
    
    #
    # have to be more clever
    #
    
    return None

