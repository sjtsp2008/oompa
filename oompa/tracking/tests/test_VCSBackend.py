#
# test_VCSBackend.py
#

import os
import unittest

from oompa.tracking.VCSBackend import VCSBackend


class VCSBackendTests(unittest.TestCase):

    def test_determine_project_name(self):

        test_cases = [

            ( "http://git.code.sf.net/p/guitarix/git",             "guitarix" ),
            ( "http://git.code.sf.net/p/guitarix/git guitarix",    "guitarix" ),   # i think this is specifying an alternate name

            ( "https://github.com/drewbuschhorn/gmail_imap.git",   "gmail_imap" ),

            ( "https://somewhere-else.com/projects/project.git",   "project" ),

            ( "git://roundup.git.sourceforge.net/gitroot/roundup", "roundup" ),

            # note that this *could* be git
            ( "https://bitbucket.org/genericcontainer/goblin-camp", "goblin-camp" ),

            ( "http://openblox.hg.sourceforge.net:8000/hgroot/openblox/openblox", "openblox" ),
            
            ( "http://freshfoo.com/repos/imapclient/trunk",            "trunk"      ),
            ( "http://freshfoo.com/repos/imapclient/trunk imapclient", "imapclient" ),
            ( "http://freshfoo.com/repos/imapclient",                  "imapclient" ),

            ( "http://hg.python.org/jython",                "jython" ),
            
            # note that this one is not a vcs url, will be rejected by
            # determine_vcs_type.  but we just follow simple rules here
            #
            ( "http://some-web-site.org/some/project",      "project" ),

            ( "https://svn.sf.net/projects/blah",                  "blah" ),
            
            ]

        vcs_backend = VCSBackend()

        for test_case in test_cases:

            if test_case is None:
                print("breaking early")
                break

            source_spec  = test_case[0]
            expected     = test_case[1]

            project_name = vcs_backend._determine_project_name(source_spec)

            # XXX need something like test_utils.assertEqualOrDumpMismatch()
            
            if project_name != expected:
                print("XXX mismatch:")
                print("  source_spec:  %s" % source_spec)
                print("  expected:     %s" % expected)
                print("  project_name: %s" % project_name)
                pass
                
            assert project_name == expected
            # self.assert(
            
            pass

        return

    pass


