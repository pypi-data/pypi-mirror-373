import pandas as pd
from luxorasap.utils.storage import BlobParquetClient

def test_write_and_read_roundtrip(fake_blob):
    client = BlobParquetClient(container="luxtest")
    df_in = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    client.write_df(df_in, "tmp/table.parquet")
    df_out, _ = client.read_df("tmp/table.parquet")
    pd.testing.assert_frame_equal(df_in, df_out)