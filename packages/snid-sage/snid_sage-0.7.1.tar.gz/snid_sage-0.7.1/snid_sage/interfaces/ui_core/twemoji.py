"""
UI Core Twemoji Facade
----------------------

Re-exports the Twemoji manager for consistent emoji rendering across GUIs.
"""

from typing import Any


def get_twemoji_manager(*args, **kwargs) -> Any:
    from snid_sage.interfaces.gui.utils.twemoji_manager import get_twemoji_manager as _get

    return _get(*args, **kwargs)


