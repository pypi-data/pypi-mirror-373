"""
Using cloudpickle for serialization but pickle for deserialization
in order to be compatible with ``pickle_module`` parameter of the ``torch.save`` method.
(cloudpickle does not include `Unpickler` in its namespace, which is required by PyTorch for deserialization)
"""

from pickle import Unpickler  # noqa: F401 # nosec B403

from cloudpickle import *  # noqa: F401, F403
from cloudpickle import CloudPickler as Pickler  # noqa: F401
