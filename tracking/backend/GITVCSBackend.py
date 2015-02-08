#
# GITVCSBackend.py
#

import io
import os

from oompa.tracking.ExecVCSBackend import ExecVCSBackend


class GITVCSBackend(ExecVCSBackend):

    _type = 'git'

    def checkout(self, source_spec, *args):
        """

        """
        
        print("%s.checkout(): %s, %r" % ( self.__class__.__name__, source_spec, args ))

        # XXX option to check into some specific folder/category

        project_name         = self._determine_project_name(source_spec)

        print("  project name: %s" % project_name)
        
        # assuming in current folder
        base_folder          = os.getcwd()
        vcs_path             = self._create_vcs_folder(project_name, base_folder)

        self.push_folder(vcs_path)

        cmd = "%s clone %s %s" % ( self._type, source_spec, " ".join(args))

        print("  cmd: %s" % project_name)

        result = self._run(cmd)

        if result != 0:
            print("  XXX something wrong?  result: %s" % result)
            print("      cd %s; %s" % ( vcs_path, cmd ))
            pass

        folder       = self.pop_folder()

        project_path = os.path.dirname(vcs_path)

        return project_path


    def update(self, project):
        """

        run git pull (all branches of origin)
        """

        # XXX need to update the constructor
        self._out_stream = project._out_stream

        vcs_folder = project.get_vcs_folder()
        vcs_type   = self._type

        if self.verbose:
            self.print("cd %s" % vcs_folder)
            pass

        self.push_folder(vcs_folder)

        child_stdout  = io.BytesIO()
        child_stderr  = self.STDOUT

        command = '%s pull' % self._type

        result  = self._run(command, 
                            stdout = child_stdout,
                            stderr = child_stderr)

        if result != 0:
            self.print("  pull result: %s" % result)
            pass

        self._dump_output(child_stdout, self._out_stream)

        self.pop_folder()

        return result


    def _clean_up_output(self, cmd_output):
        """
        cmd_output is ext

        returns text

        TODO:
          - can generalize - just a list of patterns to skip
        """

        lines = []

        for line in cmd_output.splitlines():
            if line.startswith("Already up-to-date."):
                continue
            lines.append(line)
            pass

        return "\n".join(lines).strip()


    def getSourceURL(self, project):

        config_path = os.path.join(project.get_vcs_folder(), ".git", "config")

        # XXX gross
        for line in open(config_path):
            
            line = line.strip()

            if line and line.startswith("url ="):
                pieces = line.split()
                return pieces[2]

            pass

        return

    pass
