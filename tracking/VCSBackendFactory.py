#
# VCSBackendFactory.py
#

"""

support for loading a VCSBackend that can speak the right "protocol"
(usually exec'ed commands)

TODO: 
    - use/extend the pyvcs framework
"""

import os
import subprocess

from oompa.tracking                             import file_utils

from oompa.tracking.VCSBackend                  import VCSBackend
from oompa.tracking.ExecVCSBackend              import ExecVCSBackend

from oompa.tracking.backend.MercurialVCSBackend import MercurialVCSBackend
from oompa.tracking.backend.SVNVCSBackend       import SVNVCSBackend
from oompa.tracking.backend.GITVCSBackend       import GITVCSBackend


# XXX use a plugin-discovering, class-loading, caching, registry
backend_registry = {
}

backend_classes = [ 
    SVNVCSBackend,
    MercurialVCSBackend,
    GITVCSBackend,
    ]

for backend_class in backend_classes:
    backend_registry[backend_class._type] = backend_class
    pass


def get_backend(project_type = None,
                project      = None,
                logger       = None):
    """
    project_type is a string, like 'svn'

    project is a Project
    """

    if project_type is None:
        project_type = project.project_type
        pass

    klass = backend_registry.get(project_type)

    if not klass:
        return None

    return klass(logger = logger)

