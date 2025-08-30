import pandas as pd
import datetime as dt
from pathlib import Path
from luxorasap.ingest.legacy_local.dataloader import DataLoader

def test_load_table_if_modified(tmp_path):
    (tmp_path / "parquet").mkdir(exist_ok=True)
    dl = DataLoader(luxorDB_directory=tmp_path)
    df1 = pd.DataFrame({"a":[1,2]})
    ts1 = dt.datetime.timestamp(dt.datetime.now())
    dl.load_table_if_modified(
        "test",
        df1,
        ts1,
        do_not_load_excel=True
    )
    # arquivo parquet deve existir
    pq_file = tmp_path/"parquet"/"test.parquet"
    assert pq_file.exists()
    df_saved = pd.read_parquet(pq_file)
    assert len(df_saved)==2