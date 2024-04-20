from __future__ import annotations
from typing import TYPE_CHECKING, Any

from pydavinci.connect import get_resolve

if TYPE_CHECKING:
    from pydavinci.wrappers._resolve_stubs import PyRemoteResolve

class ResolveInstanceContext(object):
    pass

class ResolveInstance:
    def __add__(self, other: PyRemoteResolve) -> PyRemoteResolve:
        """
        Assign PyRemoteResolve type.
        """
        pass

    def __init__(self):
        ResolveInstance.resolve = get_resolve()
        ResolveInstance.context = ResolveInstanceContext()

    def __getattr__(self, name) -> Any:
        return getattr(ResolveInstance.resolve, name)
    
    def __setattr__(self, name) -> Any:
        return setattr(ResolveInstance.resolve, name)


resolve_obj: PyRemoteResolve = ResolveInstance()

pydavinci_context: ResolveInstanceContext = resolve_obj.context