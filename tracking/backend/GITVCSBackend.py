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

        # TODO option to check into some specific folder/category

        # XXX stop assuming current folder
        base_folder          = os.getcwd()
        project_name         = self._determine_project_name(source_spec)
        vcs_path             = self._create_vcs_folder(project_name, base_folder)

        self.push_folder(vcs_path)

        cmd = "%s clone %s %s" % ( self._type, source_spec, " ".join(args))

        print("  cmd:      %s" % cmd)

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

        # project.log("updating %s" % ( self.path, ))
        
        vcs_folder = project.get_vcs_folder()
        vcs_type   = self._type

        showedProject = False
        
        if self.verbose:
            self.log("updating %s" % ( self.path, ))
            self.log("  cd %s" % vcs_folder)
            showedProject = True
            pass

        self.push_folder(vcs_folder)

        child_stdout  = io.BytesIO()
        child_stderr  = self.STDOUT

        command = '%s pull' % self._type

        result  = self._run(command, 
                            stdout = child_stdout,
                            stderr = child_stderr)

        if result != 0:
            project.log("  XXX pull result: %s" % result)
            project.log()
            pass

        child_out = self._getChildOutput(child_stdout)

        if child_out:
            if not showedProject:
                project.log("updating %s" % ( project.path, ))
                pass
            project.log()
            project.log(child_out)
            project.log()
            pass

        # project.dump_output(child_stdout)

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
