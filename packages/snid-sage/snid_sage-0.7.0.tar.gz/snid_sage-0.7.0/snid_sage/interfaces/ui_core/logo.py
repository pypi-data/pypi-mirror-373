"""
UI Core Logo Facade
-------------------

Provides access to the application logo/icon path used across GUIs.
"""

from typing import Any


def get_logo_manager() -> Any:
    try:
        from snid_sage.interfaces.gui.utils.logo_manager import get_logo_manager as _get

        return _get()
    except Exception:
        # Fallback stub with a compatible API
        class _StubLogoManager:
            def get_icon_path(self):
                return None

        return _StubLogoManager()


