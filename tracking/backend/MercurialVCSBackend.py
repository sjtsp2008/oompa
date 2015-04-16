#
# MercurialVCSBackend.py
#

"""
package oompa.tracking.backend
"""

import io
import os
import sys

from oompa.tracking.ExecVCSBackend import ExecVCSBackend

class MercurialVCSBackend(ExecVCSBackend):
    """

    subclass of VCSBackend that implements mercurial (hg) interaction

    """

    _type = 'hg'


    def _get_branch(self, chunk):

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

        # this is getting very specialized/complicated - 
        # aggregating summaries by branch, or change set, if
        # no branch specified

        # list of hash tables
        # chunks    = []

        by_branch = {}

        # current chunk
        chunk  = {}

        for line in cmd_output.splitlines():

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
        
        # assuming in to current folder
        project_name         = self._determine_project_name(source_spec)
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
            xxx

        folder       = self.pop_folder()

        project_path = os.path.dirname(vcs_path)

        return project_path



    def update(self, project):
        """
        """

        
        #
        # note that updating in hg, with useful output, is actually
        # two steps (because a simple update does not report what
        # actually changed).  first we use "incoming" to determine
        # if there are changes.  then we use pull --update to 
        # actually get the changes
        #

        vcs_folder    = project.get_vcs_folder()

        showedProject = False
        
        if self.verbose:
            project.log("MercurialVCSBackend.update(): %s" % ( project.path, ))
            project.log("  cd %s" % vcs_folder)
            showedProject = True
            pass

        
        self.push_folder(vcs_folder)

        child_stdout  = io.BytesIO()
        child_stderr  = self.STDOUT

        #
        # "hg pull --update" does not report what was actually
        #    updated, so we have to check with "hg incoming" first
        #
        # returns 0 if anything incoming, 1 if nothing
        #
        # TODO: capture the output of incoming, and if 
        #

        command = '%s incoming' % self._type
        result  = self._run(command, 
                            stdout = child_stdout,
                            stderr = child_stderr)

        if result == 0:

            #
            # there are differences.  now really pull them
            #

            if not showedProject:
                project.log("UPDATING %s" % ( project.path, ))
                pass
            project.log()
            project.log(self._getChildOutput(child_stdout))
            project.log()

            child_stdout  = io.BytesIO()
            child_stderr  = child_stderr

            command = '%s pull --update' % self._type

            result  = self._run(command,
                                stdout = child_stdout,
                                stderr = child_stderr)

            if result != 0:
                project.log("  XXX something wrong?  hg pull result: %s" % result)
                project.log("      cd %s; %s" % ( vcs_folder, command ))
                # XXX what about stderr?
                project.log(self._getChildOutput(child_stdout))
                project.log()
                pass
            pass

        self.pop_folder()
        return

    def getSourceURL(self, project):

        config_path = os.path.join(project.get_vcs_folder(), ".hg", "hgrc")

        # XXX gross
        for line in open(config_path):
            
            line = line.strip()

            if line and line.startswith("default ="):
                pieces = line.split()
                return pieces[2]

            pass

        return


    pass
