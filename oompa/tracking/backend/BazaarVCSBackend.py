#
# BazaarVCSBackend.py
#

"""
package oompa.tracking.backend
"""

import io
import os


from oompa.tracking.ExecVCSBackend import ExecVCSBackend

class BazaarVCSBackend(ExecVCSBackend):
    """

    subclass of VCSBackend that implements bazaar (bzr) interaction

    """

    _type = 'bzr'


    def _get_branch(self, chunk):
        """
        XXX what is chunk?
        """

        branch = chunk.get("branch")
        
        if branch is None:
            branch = chunk.get("changeset")
            if branch is None:
                xxx
                pass
            pass
        
        assert len(branch) == 1
        
        branch = branch[0]
        
        return branch


    def _clean_up_output(self, cmd_output):
        """

        """

        # print("_clean_up_output()")

        # this is getting very specialized/complicated - 
        # aggregating summaries by branch, or change set, if
        # no branch specified

        # list of hash tables
        # chunks    = []

        by_branch = {}

        # current chunk
        chunk  = {}

        for line in cmd_output.splitlines():

            # print("L: %r" % line)

            if not line:
                if not chunk:
                    continue

                branch = self._get_branch(chunk)

                by_branch.setdefault(branch, []).append(chunk)                

                chunk = {}

                continue

            # TODO: i think most of these should be optional -
            #       maybe someone else could track pedigree from the
            #       ids, ...

            if line.startswith("comparing with "):
                continue
            if line.startswith("searching for changes"):
                continue

            # strip off ending colon
            tokens = line.split()
            tag    = tokens[0][:-1] 

            # XXX hack, just because pypy is so high-velocity.
            #     this should *not* apply to all hg projects
            #     i really want this to be a function - lift all
            #     changes to a single branch ...
            
            # XXX we don't currently know our source
            # if self.source == "pypy":
            if tag == "user":
                continue
            if tag == "date":
                continue

            rest   = " ".join(tokens[1:])

            chunk.setdefault(tag, []).append(rest)
            pass

        if chunk:

            branch = self._get_branch(chunk)
            
            by_branch.setdefault(branch, []).append(chunk)                
            pass

        lines = []

        branches = by_branch.keys()
        branches = list(branches)

        branches.sort()

        for branch in branches:

            # print "branch: %s" % branch

            lines.append("branch:   %s" % branch)

            chunks = by_branch[branch]

            for chunk in chunks:

                # print "  CHUNK: %r" % chunk
                summary = chunk.get("summary")
                
                for line in summary:
                    lines.append("  summary: %s" % line)
                    pass
                pass

            lines.append("")
            pass

        return "\n".join(lines)


    def checkout(self, source_spec, *args):
        """

        checks out a project in to <project-name>/<vcs-type>/...

        project name is derived from source spec

        returns project folder that 

        """

        print("%s.checkout(): %s, %r" % ( self.__class__.__name__, source_spec, args ))
        
        project_name         = self._determine_project_name(source_spec)
        
        xxx

        # assuming in current folder
        base_folder          = os.getcwd()

        vcs_path             = self._create_vcs_folder(project_name, base_folder)

        self.push_folder(vcs_path)

        # XXX option to check into some specific folder/category

        cmd    = "%s clone %s %s" % ( self._type, source_spec, " ".join(args))

        print("  cmd: %s" % cmd)

        result = self._run(cmd)

        # 
        # process = subprocess.Popen(cmd, shell = True)
        # result  = process.wait()

        if result != 0:
            print("  XXX something wrong?  result: %s" % result)
            print("      cd %s; %s" % ( vcs_folder, cmd ))
            pass

        folder       = self.pop_folder()

        project_path = os.path.dirname(vcs_path)

        return project_path


    def _get_update_cmd(self, project):

        # assuming we are in the right folder
        cmd = '%s merge' % self._type

        return cmd

    def update(self, project):
        """
        TODO: refactor - this is now exactly the same code as SVNVCSBackend
        """

        vcs_folder = project.get_vcs_folder()

        self.push_folder(vcs_folder)

        stdout  = io.BytesIO()
        stderr  = self.STDOUT

        cmd     = self._get_update_cmd(project)
        
        result  = self._run(cmd, 
                            stdout = stdout,
                            stderr = stderr)

        self._dump_output(stdout)

        if result != 0:
            print("  XXX something wrong?  result: %s" % result)
            print("      cd %s; %s" % ( vcs_folder, cmd ))
            pass

        self.pop_folder()

        return

    pass
