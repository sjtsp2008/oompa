#
# test_vcs_utils.py
#

import os
import unittest

from oompa.tracking import vcs_utils


class vcs_utilsTests(unittest.TestCase):

    def testdetect_vcs_type_from_source(self):

        test_cases = [

            ( "https://svn.sf.net/projects/blah",                  "svn" ),
            
            ( "https://github.com/drewbuschhorn/gmail_imap.git",   "git" ),

            ( "https://somewhere-else.com/projects/project.git",   "git" ),

            ( "git://roundup.git.sourceforge.net/gitroot/roundup", "git" ),

            ( "http://git.code.sf.net/p/guitarix/git",             "git" ),
            ( "http://git.code.sf.net/p/guitarix/git guitarix",    "git" ),   # i think this is specifying an alternate name


            # note that this *could* be git
            ( "https://bitbucket.org/genericcontainer/goblin-camp", "hg" ),

            ( "http://openblox.hg.sourceforge.net:8000/hgroot/openblox/openblox", "hg" ),
            
            ( "http://freshfoo.com/repos/imapclient/trunk", "hg" ),
            ( "http://freshfoo.com/repos/imapclient",       "hg" ),

            ( "http://hg.python.org/jython",                "hg" ),

            ( "http://some-web-site.org/some/project",      None ),

            ]

        for test_case in test_cases:

            if test_case is None:
                print "breaking early"
                break

            source_spec = test_case[0]
            expected    = test_case[1]

            result      = vcs_utils.detect_vcs_type_from_source(source_spec)

            # XXX need something like test_utils.assertEqualOrDumpMismatch()
            
            assert result == expected
            # self.assert(

            
            pass


        return

    pass


