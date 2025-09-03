######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.2                                                                                 #
# Generated on 2025-09-03T10:37:45.809234                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

