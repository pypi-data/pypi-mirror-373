"""Exporta a API “cloud” por padrão e mantém DataLoader legado disponível."""

from importlib import import_module
from warnings import warn

# API moderna (recomendada)
from .cloud import save_table, incremental_load, TableDataLoader  # noqa: F401

__all__ = ["save_table", "incremental_load", "TableDataLoader"]

# Ponte para o loader antigo -------------------------------------------------
try:
    legacy_mod = import_module(".legacy_local.dataloader", __name__)
    DataLoader = legacy_mod.DataLoader  # noqa: F401
    warn(
        "luxorasap.ingest.DataLoader está legado e será descontinuado; "
        "migre para luxorasap.ingest.save_table / incremental_load.",
        DeprecationWarning,
        stacklevel=1,
    )
except Exception:
    # se o arquivo legado não existir, simplesmente não exporta
    pass