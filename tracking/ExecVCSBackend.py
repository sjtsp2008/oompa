#
# ExecVCSBackend.py
#

import os
import subprocess
import sys
import tempfile

from io import StringIO

from oompa.tracking.VCSBackend import VCSBackend



class ExecVCSBackend(VCSBackend):
    """
    base class for any subprocess-based backends
    (i.e., we run by executing commands, like "hg incoming")

    """

    # just so subclasses do not have to import subprocess
    STDOUT = subprocess.STDOUT


    def print(self, message = None):

        if message is None:
            message = ""
            pass

        self._out_stream.write("%s\n" % message)
        
        return
        


    def _run(self, 
             command,
             stdout = None,
             stderr = None):
        """
        run the specified command

        currently, stdout and sterr are not captured nor redirected

        TODO:
            - pass in streams for stdout, stderr
        """
        
        if self.verbose:
            print(command)
            pass

        # i think i'm using shell = True so that the commands match exactly
        # what i would type in a shell

        if stdout is not None:
            # i believe this file cleans itself up
            _stdout = tempfile.TemporaryFile()
        else:
            _stdout = None
            pass

        process = subprocess.Popen(command, 
                                   shell  = True,
                                   stdout = _stdout,
                                   stderr = stderr)
        result  = process.wait()

        if stdout is not None:

            # have to rewind
            _stdout.seek(0)

            stdout.write(_stdout.read())
            pass

        return result
        

    def update(self, project):
        """
        XXX works for cvs and svn, but probably should not be here anyway - should
            be in subclasses
        """

        vcs_folder = project.get_vcs_folder()
        vcs_type   = self._type

        orig_wd = os.getcwd()
        cmd     = "%s update" % vcs_type
        
        if self.verbose:
            print("cd %s" % vcs_folder)
            pass

        os.chdir(vcs_folder)

        result = self._run(cmd)

        if result != 0:
            print("  XXX something wrong?  result: %s" % result)
            print("      cd %s; %s" % ( vcs_folder, cmd ))
            pass

        os.chdir(orig_wd)

        return

    def _clean_up_output(self, output):
        """
        default is to do nothing

        output is text

        returns text

        TODO: probably need to know "output from what?"
        """

        return output


    def _dump_output(self, child_stdout, out_stream = None):
        """

        clean up and possibly print output from a child process.
        
        subclasses can implement _clean_up_output to remove noise, and
        the final string is stripped, so may possibly be empty

        stdout is an io.bytes
        """

        if out_stream is None:
            out_stream = sys.stdout

            # XXX cheating.
            self._out_stream = out_stream
            pass

        output = child_stdout.getvalue().decode("utf-8")
        output = self._clean_up_output(output)

        if output:
            self.print()
            self.print(output)
            self.print()
            pass

        return

    pass

