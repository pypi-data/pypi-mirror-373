import datetime as dt
from types import SimpleNamespace
from datetime import timezone

import pytest

from luxorasap.utils.storage import BlobChangeWatcher, BlobMetadata


# ------------------------ Fakes do SDK Azure ------------------------

class FakeDownload:
    def __init__(self, content: bytes):
        self._content = content
    def readall(self):
        return self._content

class FakeBlobClient:
    def __init__(self, name, props=None, store=None):
        self._name = name
        self._props = props  # SimpleNamespace(last_modified, etag, size)
        self._store = store  # dict[name] -> bytes (pkl snapshot)
    def get_blob_properties(self):
        if self._props is None:
            from azure.core.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError("not found")
        return self._props
    def download_blob(self, lease=None):
        # apenas para o snapshot (state pickle)
        data = self._store.get(self._name, b"")
        return FakeDownload(data)

class FakeContainerClient:
    def __init__(self, blobs, store):
        # blobs: dict[name] -> SimpleNamespace(last_modified, etag, size)
        self._blobs = blobs
        self._store = store
    def get_blob_client(self, name):
        props = self._blobs.get(name)
        return FakeBlobClient(name, props=props, store=self._store)
    def list_blobs(self, name_starts_with=""):
        for name, props in self._blobs.items():
            if name.startswith(name_starts_with):
                # Azure devolve itens com .name + props
                item = SimpleNamespace(
                    name=name,
                    last_modified=props.last_modified,
                    etag=props.etag,
                    size=props.size,
                )
                yield item
    def upload_blob(self, name, data, overwrite=False):
        # usado para salvar o snapshot .pkl
        content = data.read() if hasattr(data, "read") else data
        self._store[name] = content
        return SimpleNamespace()  # dummy

class FakeBlobServiceClient:
    def __init__(self, container_client):
        self._cc = container_client
    def get_container_client(self, container):
        return self._cc

# ------------------------ Fixtures ------------------------

@pytest.fixture
def fake_now():
    return dt.datetime(2025, 8, 25, 12, 0, 0, tzinfo=timezone.utc)

@pytest.fixture
def azure_mocks(monkeypatch, fake_now):
    """
    Prepara um container fake com 2 blobs e storage em memória para o snapshot pkl.
    """
    # blobs existentes no "ADLS"
    blobs = {
        "raw/x/a.xlsx": SimpleNamespace(
            last_modified=fake_now, etag='"v1-a"', size=100
        ),
        "raw/p/tb.parquet": SimpleNamespace(
            last_modified=fake_now, etag='"v1-p"', size=500
        ),
    }
    # storage em memória para o snapshot .pkl
    store = {}

    cc = FakeContainerClient(blobs=blobs, store=store)
    bsc = FakeBlobServiceClient(container_client=cc)

    # patcha o construtor real para devolver o fake
    import luxorasap.utils.storage.change_tracker as mod
    monkeypatch.setattr(mod, "BlobServiceClient", SimpleNamespace(from_connection_string=lambda *_args, **_kw: bsc))

    return SimpleNamespace(blobs=blobs, store=store, cc=cc, bsc=bsc)


# ------------------------ Testes ------------------------


def test_no_change_is_false(azure_mocks):
    watcher = BlobChangeWatcher(
        container="luxorasap",
        snapshot_blob_path="system/state/tests",
        watcher_id='test_watcher.pkl',
        treat_missing_as_changed=True,
    )
    # primeira vez -> muda
    watcher.has_changed("raw/p/tb.parquet", update_snapshot=True)

    # mesma versão -> não muda
    changed, prev, curr = watcher.has_changed("raw/p/tb.parquet", update_snapshot=False)
    assert changed is False
    assert prev is not None and curr is not None
    assert prev.etag == curr.etag
    assert prev.size_bytes == curr.size_bytes


def test_change_by_etag_or_size_is_true(monkeypatch, azure_mocks, fake_now):
    watcher = BlobChangeWatcher(
        container="luxorasap",
        snapshot_blob_path="system/state/tests",
        watcher_id='test_watcher.pkl'
    )
    # baseline
    watcher.has_changed("raw/x/a.xlsx", update_snapshot=True)

    # muda etag
    azure_mocks.blobs["raw/x/a.xlsx"].etag = '"v2-a"'
    changed, prev, curr = watcher.has_changed("raw/x/a.xlsx", update_snapshot=False)
    assert changed is True

    # aplica snapshot
    watcher.has_changed("raw/x/a.xlsx", update_snapshot=True)

    # muda apenas tamanho
    azure_mocks.blobs["raw/x/a.xlsx"].size = 200
    changed2, _, _ = watcher.has_changed("raw/x/a.xlsx", update_snapshot=False)
    assert changed2 is True


def test_deleted_blob_is_considered_changed_if_was_known(azure_mocks):
    watcher = BlobChangeWatcher(
        container="luxorasap",
        snapshot_blob_path="system/state/tests",
        watcher_id='test_watcher.pkl'
    )
    # primeiro registra
    watcher.has_changed("raw/p/tb.parquet", update_snapshot=True)

    # remove do conjunto remoto
    azure_mocks.blobs.pop("raw/p/tb.parquet")

    changed, prev, curr = watcher.has_changed("raw/p/tb.parquet", update_snapshot=True)
    assert changed is True
    assert prev is not None
    assert curr is None  # não existe mais


def test_list_changed_under_prefix_filters_and_updates(azure_mocks, fake_now):
    watcher = BlobChangeWatcher(
        container="luxorasap",
        snapshot_blob_path="system/state/tests",
        watcher_id='test_watcher.pkl'
    )
    # primeira varredura (primeira vez conta como mudança)
    changed = watcher.list_changed_under_prefix(
        "raw/",
        allowed_extensions=[".xlsx"],
        update_snapshot=True,
    )
    assert changed == ["raw/x/a.xlsx"]

    # altera parquet, mas filtro é xlsx, então não deve aparecer
    azure_mocks.blobs["raw/p/tb.parquet"].etag = '"v2-p"'
    changed2 = watcher.list_changed_under_prefix(
        "raw/",
        allowed_extensions=[".xlsx"],
        update_snapshot=True,
    )
    assert changed2 == []
