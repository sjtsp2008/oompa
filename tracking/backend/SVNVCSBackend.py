#
# SVNVCSBackend.py
#

"""
package oompa.tracking
"""

import io
import os
import urllib

from oompa.tracking.ExecVCSBackend import ExecVCSBackend



class SVNVCSBackend(ExecVCSBackend):
    """
    oompa backend for dealing with svn repositories
    """

    _type = 'svn'

    def checkout(self, source_spec, *args):

        print("%s.checkout(): %s, %r" % ( self.__class__.__name__, source_spec, args ))

        # get project name from final piece
        result               = urllib.parse.urlparse(source_spec)
        tail                 = os.path.basename(result.path)
        project_name, suffix = os.path.splitext(tail)
        
        # assuming in current folder
        base_folder          = os.getcwd()

        vcs_path             = self._create_vcs_folder(project_name, base_folder)

        self.push_folder(vcs_path)

        # XXX option to check into some specific folder/category

        cmd    = "%s co %s %s" % ( self._type, source_spec, " ".join(args))

        result = self._run(cmd)

        # print("  cmd: %s" % cmd)
        # 
        # process = subprocess.Popen(cmd, shell = True)
        # result  = process.wait()

        if result != 0:
            print("  XXX something wrong?  result: %s" % result)
            print("      cd %s; %s" % ( vcs_folder, cmd ))
            pass

        self.pop_folder()

        return vcs_path


    def _clean_up_output(self, output):
        """
        
        output is a string
        """

        lines = []

        for line in output.splitlines():
            if line.startswith("At revision"):
                continue
            if line.startswith("Updated to "):
                continue
            lines.append(line)
            pass

        #
        # skip bare "Updating '.' line
        #
        if len(lines) == 1 and lines[0] == "Updating '.':":
            return ""

        output = "\n".join(lines).strip()

        return output


    def _get_update_cmd(self, project):

        # assuming we are in the right folder
        cmd       = "%s update" % self._type

        return cmd


    def update(self, project):
        """
        TODO: refactor - this is now exactly the same code as BazaarVCSBackend
        """

        # XXX need to update the constructor
        self._out_stream = project._out_stream

        vcs_folder = project.get_vcs_folder()

        self.push_folder(vcs_folder)

        child_stdout  = io.BytesIO()
        child_stderr  = self.STDOUT

        cmd    = self._get_update_cmd(project)
        result = self._run(cmd,
                            stdout = child_stdout,
                            stderr = child_stderr)

        self._dump_output(child_stdout, self._out_stream)

        if result != 0:
            self.print("  XXX something wrong?  result: %s" % result)
            self.print("      cd %s; %s" % ( vcs_folder, cmd ))
            pass

        self.pop_folder()

        return result


    def getSourceURL(self, project):

        # vcs_folder  = project.get_vcs_folder()
        
        # not obvious in any ascii files - in a sqlite db
        return "???"


    pass

