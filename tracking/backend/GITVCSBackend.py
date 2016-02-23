#
# GITVCSBackend.py
#

import io
import os

from oompa.tracking.ExecVCSBackend import ExecVCSBackend


class GITVCSBackend(ExecVCSBackend):

    _type = 'git'

    def checkout(self, source_spec, *args):
        """returns the path where the project was checked out

        appears to assume that source_spec has already been identifies as git

        """
        
        self.log("%s.checkout(): %s, %r" % ( self.__class__.__name__, source_spec, args ))

        # kind of a hack, for easier integration with discovery tools and github3.py -
        # if caller has not supplied the ".git"

        if source_spec.startswith("https://github.com/") and not source_spec.endswith(".git"):
            source_spec += ".git"
            self.log("%s.checkout(): %s, %r" % ( self.__class__.__name__, source_spec, args ))
            pass
        
        # TODO option to checkout into some specific folder/category

        # XXX stop assuming current folder
        base_folder          = os.getcwd()
        project_name         = self._determine_project_name(source_spec)
        vcs_path             = self._create_vcs_folder(project_name, base_folder)

        self.push_folder(vcs_path)

        cmd = "%s clone %s %s" % ( self._type, source_spec, " ".join(args))

        self.log("  cmd:      %s" % cmd)

        result = self._run(cmd)

        if result != 0:
            self.log("  XXX something wrong?  result: %s" % result)
            self.log("      cd %s; %s" % ( vcs_path, cmd ))
            pass

        folder       = self.pop_folder()

        project_path = os.path.dirname(vcs_path)

        return project_path


    def update(self, project):
        """

        run git pull (all branches of origin)
        """

        # project.log("updating %s" % ( self.path, ))
        
        vcs_folder    = project.get_vcs_folder()

        showedProject = False
        
        if self.verbose:
            project.log("GITVCSBackend.update(): %s" % ( project.path, ))
            project.log("  cd %s" % vcs_folder)
            showedProject = True
            pass

        self.push_folder(vcs_folder)

        child_stdout  = io.BytesIO()
        child_stderr  = self.STDOUT

        command       = '%s pull' % self._type

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
                self._reportUpdatingProject(project)
                pass
            project.log()
            project.log(child_out)
            project.log()
            project.log()
            pass

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
