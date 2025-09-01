#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

"""
IBM HElayers is a software development kit (SDK) for the practical and
efficient execution of encrypted workloads using fully homomorphic encrypted
data. HElayers is designed to enable application developers and data scientists
to seamlessly apply advanced privacy-preserving techniques without requiring
specialized skills in cryptography.
"""
import os
if 'HELAYERS_RESOURCES_DIR' not in os.environ:
    os.environ['HELAYERS_RESOURCES_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)) , "resources")

from ._pyhelayerslite_cppwrappers import *
from . import _pyhelayerslite_cppwrappers

import inspect
import typing


# Declare DefaultContext as an alias to the widely used SealCkksContext
DefaultContext = SealCkksContext

__all__ = [
    'DefaultContext'
]

# Rename public objects' module name from 'pyhelayerslite._pyhelayerslite_cppwrappers'
# to 'pyhelayerslite', and expose them in __all__
for name in dir(_pyhelayerslite_cppwrappers):
    if not name.startswith('_'):
        __all__.append(name)
        obj = getattr(_pyhelayerslite_cppwrappers, name)
        if (isinstance(obj, typing.Callable) or inspect.isclass(obj)):
            if (obj.__module__ != 'pyhelayerslite'):
                obj.__module__ = 'pyhelayerslite'
