Oompa 
=====

A small orange robot to help you keep up with rapidly changing
software, and track changes across full ecosystems, and learn quickly
about new software/systems/organizations that may interest you.

It also sometimes sings bad songs regarding your character flaws.

It used to be quite ambitious - a sort of pip or yum-from-source plus
jenkins, before they existed (but never better than cheap-hack
quality).  For building Mach, BSD, and early-days Linux kernels
(starting from building libtools, assembler, glibc, kernel, X, gnome,
nautilus, ...), Flux/Flask, ...  Sometimes using a modem as network
access!  In the pre-source-control days, would track and download
(ftp) source tar.gz on ftp sites, untar, and run a project-specific
set of steps (e.g., configure, make, ...), make sure all depdendencies
were built.

Not much of that triggering/reaction/coordination is necessary any
more, and I think packages like Luigi or AirFlow could probably
replace most of the "reaction system".

Right now (201202(...201506)) it is back to simple tracking of changes
from remote svn, hg, git repositories.  And in 2015 it began
supporting tracking of "meta-github" stuff, since the trend now
appears to be spreading a single project across many different small
github repos.


Initial Supported Functionality
-------------------------------

There are fifteen years of organic growth and abandoned experiments in
here.  Some of it does not work, other might parts work with a lot of
tenacity and patience, and a microscope.  That will all be better
organized or cleaned up, if the public project gains momentum.

The main reason it's being released now is to try to build up critical
mass for the github (and beyond, possibly) "meta-discovery" system - 


Limitations
-----------

- probably only works on linux and osx
  - currently, state for the discovery system is stored in a tree of json files
    - heading toward sqlite or some cloud-hosted db, but ...
  - there is no real state for the source-tracking system - it's just the source tree
    itself
  - i use osx

- requires comfort with command-line unix.  no UI (yet)

- not yet a real python package
  - no setup.py yet
  - auto-run tests before package/publish
  
- i just copied my pylib file_utils.py in to tracking/
  - i think plain python has caught up to a lot of the crutches i wrote in pylib
  - TODO: publish pylib as a separate project, or get what i need in to someone else's project




Dependencies
------------

I'm not sure if it will run under default apple python (2).  I'm using
Anaconda Python 3 distribution.


> \# wrapper around Github REST webservices
>
> sudo pip install github3.py
> 
> \# click is a nice system for turning functions/methods in to a command/language
>
> sudo pip install click
> 
> \# is yaml included?
> 
> sudo pip install yaml
> 
> \# you won't need this right away, but in a few days/weeks, ...
>
> sudo pip install py2neo



Initial Setup
-------------

> TODO: get setup.py working
>
> TODO:   test in a from-scratch virtualenv
>
> OOMPA_HOME=$HOME/sandbox/oompa
> 
> export PYTHONPATH=$PYTHONPATH:$(dirname $OOMPA_HOME)
> 
> PATH=$PATH:$OOMPA_HOME/scripts




Github User/Org Tracking and Discovery
--------------------------------------

The "tracker discover" system keeps snapshots of the most recent
metadata state of github entities (repos/starred/follows/following for
users, public_members/repos/following/... for organizations), and will
report updates whenever you run "tracker discover".

You currently have to prime it with "tracker discover some-entity-name"
(e.g., "tracker discover linkedin")

(One of the top TODO's is to be able to dynamically seed the discover from
your github starred and following lists)


> tracker discover linkedin

> tracker discover curran


You can optionally also specify a "user/..." or "organization/..."
prefix.  Internally, all entities are explicitly either "user/..." or
"organization/..."  (e.g. "organization/netflix", "user/curran").
Most of the time, you don't have to specify the type prefix when
adding new entitites.  If the name matches both a User and
Organization, the tracker will prefer the Organization.



\# wait a day ...


> $ tracker discover

You will see each entity you are tracking, and any updates

Updates will include new_starred_repositories (and removals from
starred repositories)

Under the covers, the discovery system is really just diffing
webservice results from one snapshot to another.  it applies little or
no semantics to the contents of the list.  (which sometimes gets
annoying - a new starred_repository is "d3/d3-scale", which you will
currently have to paste on to end of "http://github.com" to check out
the project.

If there is a change to repositories for an entity, the system will
report the full github url, and attempt to summarize the first few
lines of the repo's README.md


My typical pattern is to run "tracker discover" on a semi-regular
basis, investigate some of the new repos, maybe start tracking them
with oompa (that's not yet documented), and also investigate the owner
of any repos that i like.  and i regularly add some of them to my
tracking list, ...




To remind yourself what you are tracking:

> tracker tracking



IGNORE EVERYTHING BELOW HERE, for now
=====================================


Playing with github-neo
-----------------------

github-neo is a barely-started attempt to induce seeded github
subgraphs in to neo4j and perform even cooler discoveries, like
"two-out repos starred by several people that i like"

it's not nearly ready for prime time yet

<add some notes about this.  i have not yet gotten it to perform a
full two-out crawl>



Source Code Tracking
--------------------

This was the original core of


See <some checkout/update doc that does not exist yet>

In general, it works with most git and mercurial repos.  but sometimes
it has trouble guessing the kind of repo from the url.

The github helper has special support for knowing that all repos end
with ".git".

> tracker checkout http://github.com/d3/d3.git

> tracker co http://github.com/d3/d3


  

Or check something out manually, and add it to the tracking system.
(mostly useful for stuff you had already checked out, or repos/sites
that oompa can't handle yet)

> tracker track


Run "tracker update" on a regular basis to do "pulls" (as defined by
the version control system).

All updates are logged to a file.  the reported updates are typically
all of the files that changed, versus something more useful like
github log, ...  that is gradually being cleaned up

> tracker update



Note that there is currently no "reaction system" supported (because i
haven't wanted it in a very long time)



