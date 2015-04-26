#
# test_GitHub3Helper.py
#

import os
import unittest

from oompa.tracking.github.GitHub3Helper import GitHub3Helper


class GitHub3HelperTests(unittest.TestCase):

    def testextractBlurb(self):

        # XXX not moved to correct home yet
        from oompa.tracking.github.GitHub3Helper import extractBlurb

        
        cases = [

            ( None,
              None,
              ),

            ( "",
              "",
              ),

            ( "Long enough first paragraph - \nmultiple lines\n\nParagraph 2\n\nParagraph 2",
              "Long enough first paragraph - \nmultiple lines\n...",
              ),
            
            ( "Three Paragraphs\n\nParagraph 2\n\nParagraph 3",
              "Three Paragraphs\n\nParagraph 2\n...",
              ),

            ( "One Short Paragraph",
              "One Short Paragraph",
              ),

            
            ]

        for case in cases:

            if case is None:
                print("breaking early")
                break
            
            content       = case[0]
            expectedBlurb = case[1]

            blurb         = extractBlurb(content)

            if blurb != expectedBlurb:
                print("XXX mismatch:")
                print("  content:       %r" % content)
                print("  expectedBlurb: %r" % expectedBlurb)
                print("  blurb:         %r" % blurb)
                pass
            
            assert blurb == expectedBlurb
            
            pass
        

        return

    pass
