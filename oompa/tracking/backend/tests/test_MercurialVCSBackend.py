#
#
#

import os
import unittest

from pylib.testing                              import test_utils

from oompa.tracking.backend.MercurialVCSBackend import MercurialVCSBackend


class MercurialVCSBackendTests(unittest.TestCase):

    def test_clean_up_output(self):

        test_cases = [

            ( """
comparing with https://bitbucket.org/pypy/pypy
searching for changes
changeset:   52389:21f1095789ea
parent:      52384:57f3f4d1d3c3
user:        Armin Rigo <arigo@tunes.org>
date:        Fri Jan 20 10:12:08 2012 +0100
summary:     Skip this import if it fails because of _weakref
""",
              """branch: 52389:21f1095789ea
  summary: Skip this import if it fails because of _weakref
""",
              ),
            
            # None,

            ( """
comparing with https://bitbucket.org/pypy/pypy
searching for changes
changeset:   52389:21f1095789ea
parent:      52384:57f3f4d1d3c3
user:        Armin Rigo <arigo@tunes.org>
date:        Fri Jan 20 10:12:08 2012 +0100
summary:     Skip this import if it fails because of _weakref

changeset:   52390:39fa5ecf8332
branch:      stm-gc
parent:      52388:6a3921493c66
user:        Armin Rigo <arigo@tunes.org>
date:        Sun Feb 12 12:06:57 2012 +0100
summary:     Fix for merge

changeset:   52391:dd44ce4e0cea
branch:      stm-gc
user:        Armin Rigo <arigo@tunes.org>
date:        Sun Feb 12 12:11:32 2012 +0100
summary:     Remove this hack.

changeset:   52392:f312b056bb07
branch:      stm-gc
user:        Armin Rigo <arigo@tunes.org>
date:        Sun Feb 12 12:16:44 2012 +0100
summary:     Dont need to instantiate a class to access static methods
""",
              """branch: 52389:21f1095789ea
  summary: Skip this import if it fails because of _weakref

branch: stm-gc
  summary: Fix for merge
  summary: Remove this hack.
  summary: Dont need to instantiate a class to access static methods
"""
              ),

            # None,

            #
            # degenerate case - strips off any tailing whitespace
            #
            ( """
""",
              "",
              ),
            
            # None,


            ]

        backend = MercurialVCSBackend()

        for test_case in test_cases:

            if test_case is None:
                print("breaking early")
                break

            orig_output                = test_case[0]
            expected_cleaned_up_output = test_case[1]

            cleaned_up_output = backend._clean_up_output(orig_output)

            if cleaned_up_output != expected_cleaned_up_output:
                print("ECUO")
                print("%r" % expected_cleaned_up_output)
                print("/ECUO")
                print("CUO")
                print("%r" % cleaned_up_output)
                print("/CUO")

            # XXX need to use assertEqualOrDumpMismatch - too hard to
            #     find the specific case that's a problem
            #    

            self.assertEqual(cleaned_up_output,
                             expected_cleaned_up_output)

            pass

        return

    pass

