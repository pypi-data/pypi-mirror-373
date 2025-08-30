"""
LuxorASAP – pacote raiz.

• Versão única obtida via importlib.metadata.
• Lazy-loading dos subpacotes (datareader, ingest, utils).
• Reexporta LuxorQuery para conveniência:  from luxorasap import LuxorQuery
"""

from importlib import import_module, metadata
from types import ModuleType

# ─── Versão ───────────────────────────────────────────────────────
try:
    __version__: str = metadata.version(__name__)
except metadata.PackageNotFoundError:  # editable install
    __version__ = "1.0.0"

# ─── Lazy loader ─────────────────────────────────────────────────
def __getattr__(name: str) -> ModuleType:
    if name in {"datareader", "ingest", "utils"}:
        module = import_module(f".{name}", __name__)
        globals()[name] = module            # cache no namespace
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# ─── Conveniência: import direto de LuxorQuery ───────────────────
LuxorQuery = import_module(".datareader", __name__).LuxorQuery  # type: ignore[attr-defined]

__all__ = ["__version__", "LuxorQuery"]