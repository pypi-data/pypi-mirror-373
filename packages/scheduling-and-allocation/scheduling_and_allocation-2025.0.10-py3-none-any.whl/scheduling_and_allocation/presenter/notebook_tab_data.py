# =====================================================================================
# Notebook book-keeping
# =====================================================================================
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class NBTabInfo:
        name: str
        label: str
        subpages: list = field(default_factory=list)
        frame_args: dict[str, Any] =  field(default_factory=dict)
        creation_handler: Callable = lambda *_: None
        is_default_page: bool = False

