import pandas as pd
import datetime as dt
from types import SimpleNamespace
import luxorasap.ingest.cloud as cloud


def test_save_table_calls_blob_client(fake_blob, monkeypatch):
    captured = {}
    
    def fake_write(df, path):
        captured["df"] = df.copy()
        captured["path"] = path
    
    monkeypatch.setattr(cloud, "_client", SimpleNamespace(write_df=fake_write))

    df = pd.DataFrame({"x": [1]})
    cloud.save_table("t1", df, directory="dir")
    assert captured["path"] == "dir/t1.parquet"
    assert captured["df"].equals(df.astype(str))
    

def test_incremental_load_merges_correctly(fake_blob, monkeypatch):
    # stub LuxorQuery
    prev = pd.DataFrame({"Date": [dt.date(2024,1,1)], "v":[1]})
    stub_lq = SimpleNamespace(
        table_exists=lambda n: True,
        get_table=lambda n, drop_last_updated_columns=False, **kwargs: prev
    )
    writes = {}
    monkeypatch.setattr(cloud, "_client", SimpleNamespace(write_df=lambda df, p: writes.setdefault("df", df)))
    new = pd.DataFrame({"Date":[dt.date(2024,1,2)], "v":[2]})
    cloud.incremental_load(stub_lq, "prices", new, increment_column="Date")
    assert len(writes["df"]) == 2