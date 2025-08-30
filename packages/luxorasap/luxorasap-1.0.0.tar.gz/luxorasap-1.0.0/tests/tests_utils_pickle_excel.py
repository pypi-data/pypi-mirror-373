import io
import pickle
import pandas as pd
import pytest
from types import SimpleNamespace

# Supondo que as classes estejam em luxorasap.utils.storage.blob
from luxorasap.utils.storage import BlobPickleClient, BlobExcelClient


# ------------------------ Fakes Azure ------------------------

class FakeDownload:
    def __init__(self, content: bytes):
        self._content = content
    def readall(self):
        return self._content

class FakeBlobClient:
    def __init__(self, name, store):
        self._name = name
        self._store = store
    def download_blob(self):
        if self._name not in self._store:
            from azure.core.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError("not found")
        return FakeDownload(self._store[self._name])

class FakeContainerClient:
    def __init__(self, store):
        self._store = store
    def get_blob_client(self, name):
        return FakeBlobClient(name, self._store)
    def upload_blob(self, name, data, overwrite=False):
        content = data.read() if hasattr(data, "read") else data
        self._store[name] = content
        return SimpleNamespace()

class FakeBlobServiceClient:
    def __init__(self, container_client):
        self._cc = container_client
    def get_container_client(self, container):
        return self._cc

# ------------------------ Fixtures ------------------------

@pytest.fixture
def mem_store():
    return {}

@pytest.fixture
def patch_blob_clients(monkeypatch, mem_store):
    # Patch para BlobPickleClient / BlobExcelClient usarem o FakeBlobServiceClient
    import luxorasap.utils.storage.blob as mod
    fake_bsc = FakeBlobServiceClient(FakeContainerClient(mem_store))
    monkeypatch.setattr(mod, "BlobServiceClient", SimpleNamespace(from_connection_string=lambda *_a, **_k: fake_bsc))
    return mem_store

# ------------------------ Tests Pickle ------------------------

def test_pickle_roundtrip(patch_blob_clients):
    client = BlobPickleClient()
    obj = {"a": 1, "b": [1, 2, 3]}
    path = "aux/test/state.pkl"

    client.write_pickle(obj, path)
    loaded = client.read_pickle(path)
    assert loaded == obj

def test_pickle_read_missing_raises(monkeypatch, patch_blob_clients):
    client = BlobPickleClient()
    with pytest.raises(Exception):
        client.read_pickle("aux/missing.pkl")

# ------------------------ Tests Excel ------------------------

@pytest.mark.skipif(
    pytest.importorskip("openpyxl", reason="openpyxl é necessário para testar Excel") is None,
    reason="openpyxl não disponível",
)
def test_excel_roundtrip(patch_blob_clients, tmp_path):
    df = pd.DataFrame({"Nome": ["Ana", "Bruno"], "Idade": [28, 35]})
    client = BlobExcelClient()

    blob_path = "reports/teste.xlsx"
    client.write_excel(df, blob_path, index=False)

    df2 = client.read_excel(blob_path)
    # Comparação tolerante a tipos (pandas pode alterar dtype ao ler)
    assert df2.shape == df.shape
    assert list(df2.columns) == list(df.columns)
    assert df2.astype(str).equals(df.astype(str))
