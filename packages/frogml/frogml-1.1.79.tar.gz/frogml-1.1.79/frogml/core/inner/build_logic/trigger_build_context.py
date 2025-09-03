from __future__ import annotations

from dataclasses import dataclass

from frogml.core.inner.build_logic.interface.context_interface import Context


@dataclass
class TriggerBuildContext(Context):
    pass
