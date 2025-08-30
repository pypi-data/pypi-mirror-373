import pandas as pd
from luxorasap.utils.dataframe import prep_for_save

def test_prep_for_save_index_and_normalize():
    df = pd.DataFrame({"Nome": [" ABC ", "dEf "]}, index=[10, 11])
    out = prep_for_save(df, index=True, index_name="ID", normalize=True)
    assert "ID" in out.columns
    assert out.loc[0, "Nome"] == "abc"