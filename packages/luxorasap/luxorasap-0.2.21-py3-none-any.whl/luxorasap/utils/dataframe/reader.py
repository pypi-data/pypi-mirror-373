import io, pandas as pd, pyarrow.parquet as pq

def read_bytes(buf: bytes, *, filename: str) -> pd.DataFrame:
    """Detecta a extensão e carrega em DataFrame."""
    ext = filename.split(".")[-1].lower()
    f = io.BytesIO(buf)

    if ext in {"xlsx", "xls"}:
        return pd.read_excel(f)
    if ext == "parquet":
        return pq.read_table(f).to_pandas()
    if ext == "csv":
        try:
            return pd.read_csv(f, encoding="utf-8")
        except UnicodeDecodeError:
            f.seek(0)
            return pd.read_csv(f, encoding="latin1")

    raise ValueError(f"Extensão {ext} não suportada")
