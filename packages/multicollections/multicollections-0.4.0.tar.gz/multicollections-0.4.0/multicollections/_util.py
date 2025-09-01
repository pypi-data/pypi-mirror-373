import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

if sys.version_info >= (3, 12):
    from typing import override
else:
    try:
        from typing_extensions import override
    except ImportError:  # pragma: nocover
        if TYPE_CHECKING:
            raise

        def override(func: Callable) -> Callable:
            """Fallback override decorator that does nothing."""
            return func


__all__ = ["override"]
