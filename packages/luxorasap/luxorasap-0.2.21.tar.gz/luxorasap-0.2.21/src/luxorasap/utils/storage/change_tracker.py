from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

# Reuso dos utilitários que você já tem no projeto
from luxorasap.utils.storage.blob import BlobPickleClient
import os


# ──────────────────────────────────────────────────────────────────────────────
# Tipos de dados
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class BlobMetadata:
    """
    Conjunto mínimo de informações para detectar mudanças em um blob.
    """
    last_modified_utc: datetime   # timezone-aware, sempre em UTC
    etag: str
    size_bytes: int

    @staticmethod
    def from_blob_properties(props) -> "BlobMetadata":
        """
        Constrói BlobMetadata a partir de BlobProperties (SDK azure.storage.blob).
        Garante que last_modified seja timezone-aware em UTC.
        """
        last_mod = props.last_modified
        if last_mod.tzinfo is None:
            last_mod = last_mod.replace(tzinfo=timezone.utc)
        else:
            last_mod = last_mod.astimezone(timezone.utc)

        return BlobMetadata(
            last_modified_utc=last_mod,
            etag=props.etag,
            size_bytes=int(props.size),
        )

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["last_modified_utc"] = self.last_modified_utc.isoformat()
        return d

    @staticmethod
    def from_dict(d: Dict) -> "BlobMetadata":
        lm = d["last_modified_utc"]
        if isinstance(lm, str):
            lm = datetime.fromisoformat(lm)
        if lm.tzinfo is None:
            lm = lm.replace(tzinfo=timezone.utc)
        else:
            lm = lm.astimezone(timezone.utc)
        return BlobMetadata(last_modified_utc=lm, etag=d["etag"], size_bytes=int(d["size_bytes"]))


# ──────────────────────────────────────────────────────────────────────────────
# Watcher (com persistência em pickle no próprio ADLS)
# ──────────────────────────────────────────────────────────────────────────────

class BlobChangeWatcher:
    """
    Verificador de mudanças de blobs, com snapshot persistido via Pickle no ADLS.

    Snapshot salvo como dict:
        {
          "<blob_path>": {"last_modified_utc": "...", "etag": "...", "size_bytes": int},
          ...
        }
    """

    def __init__(
        self,
        *,
        adls_connection_string: Optional[str] = None,
        container: str = "luxorasap",
        snapshot_blob_path: str = "system/state",
        watcher_id: str = "blob_change_watcher.pkl",
        treat_missing_as_changed: bool = True,
    ) -> None:
        """
        Args:
            adls_connection_string: Se None, usa AZURE_STORAGE_CONNECTION_STRING do ambiente.
            container: Nome do container onde estão os blobs (e onde ficará o snapshot).
            snapshot_blob_path: Caminho do arquivo pickle (no próprio container) que guarda o snapshot.
            treat_missing_as_changed: Se True, um blob observado pela primeira vez é considerado "mudado".
        """
        
        if adls_connection_string is None:
            adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            
        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
        
        self._container_name = container
        self._snapshot_blob_path = f"{snapshot_blob_path}/{watcher_id}"
        self._treat_missing_as_changed = treat_missing_as_changed

        # Clientes
        self._blob_service = BlobServiceClient.from_connection_string(adls_connection_string)
        self._container_client = self._blob_service.get_container_client(self._container_name)
        self._pickle_client = BlobPickleClient(
            adls_connection_string=adls_connection_string,
            container=self._container_name,
        )

        # Estado em memória
        self._snapshot: Dict[str, Dict] = {}

        # Carrega snapshot na inicialização (se não existir, começa vazio)
        self._load_snapshot()

    # ───────────────────────────── Persistência do snapshot ─────────────────────────────

    def _load_snapshot(self) -> None:
        """
        Carrega o snapshot do ADLS (pickle).
        Se não existir ou estiver inválido, inicia com dicionário vazio.
        """
        try:
            data = self._pickle_client.read_pickle(self._snapshot_blob_path)
            self._snapshot = data if isinstance(data, dict) else {}
        except FileNotFoundError:
            self._snapshot = {}
        except Exception:
            # Corrupção/versão antiga/etc → começa do zero
            self._snapshot = {}


    def _save_snapshot(self) -> None:
        """
        Salva o snapshot atual no ADLS via pickle.
        """
        self._pickle_client.write_pickle(self._snapshot, self._snapshot_blob_path)

    # ───────────────────────────── Acesso a propriedades remotas ─────────────────────────────

    def _fetch_remote_metadata(self, blob_path: str) -> BlobMetadata:
        """
        Busca metadados atuais do blob no ADLS.
        Raises:
            ResourceNotFoundError se o blob não existir.
        """
        props = self._container_client.get_blob_client(blob_path).get_blob_properties()
        return BlobMetadata.from_blob_properties(props)

    def _get_snapshot_metadata(self, blob_path: str) -> Optional[BlobMetadata]:
        """
        Retorna o metadata salvo no snapshot (se houver).
        """
        raw = self._snapshot.get(blob_path)
        return BlobMetadata.from_dict(raw) if raw else None

    # ───────────────────────────── API pública ─────────────────────────────

    def has_changed(
        self,
        blob_path: str,
        *,
        update_snapshot: bool = False,
        treat_missing_as_changed: Optional[bool] = None,
    ) -> Tuple[bool, Optional[BlobMetadata], Optional[BlobMetadata]]:
        """
        Verifica se o blob mudou desde o snapshot anterior.

        Args:
            blob_path: Caminho do blob (ex.: "raw/xlsx/trades.xlsx").
            update_snapshot: Se True, grava o novo estado no snapshot quando houver mudança.
            treat_missing_as_changed: Override local para a regra de "primeira vez conta como mudança?".

        Returns:
            (mudou?, metadata_antigo, metadata_atual)
        """
        if treat_missing_as_changed is None:
            treat_missing_as_changed = self._treat_missing_as_changed

        previous = self._get_snapshot_metadata(blob_path)

        # Se o blob não existe mais no remoto:
        try:
            current = self._fetch_remote_metadata(blob_path)
        except ResourceNotFoundError:
            changed = previous is not None
            if update_snapshot and changed:
                # remove do snapshot porque o blob foi apagado
                self._snapshot.pop(blob_path, None)
                self._save_snapshot()
            return changed, previous, None

        # Primeira observação desse blob?
        if previous is None:
            changed = bool(treat_missing_as_changed)
        else:
            # Critério de mudança (ordem de “força”: etag > last_modified > size)
            changed = (
                current.etag != previous.etag
                or current.last_modified_utc != previous.last_modified_utc
                or current.size_bytes != previous.size_bytes
            )

        if update_snapshot and changed:
            self._snapshot[blob_path] = current.to_dict()
            self._save_snapshot()

        return changed, previous, current


    def update_snapshot(self, blob_path: str) -> Optional[BlobMetadata]:
        """
        Força a atualização do snapshot para refletir o estado atual do blob.
        Se o blob não existir, remove do snapshot e retorna None.
        """
        try:
            current = self._fetch_remote_metadata(blob_path)
        except ResourceNotFoundError:
            self._snapshot.pop(blob_path, None)
            self._save_snapshot()
            return None

        self._snapshot[blob_path] = current.to_dict()
        self._save_snapshot()
        return current


    def mark_as_synchronized(self, blob_path: str, metadata: Optional[BlobMetadata] = None) -> None:
        """
        Marca explicitamente um blob como “sincronizado” no snapshot (ex.: após processar um pipeline).
        Se `metadata` não for informado, consulta o estado atual no ADLS.
        """
        if metadata is None:
            metadata = self._fetch_remote_metadata(blob_path)
        self._snapshot[blob_path] = metadata.to_dict()
        self._save_snapshot()


    def list_changed_under_prefix(
        self,
        prefix: str,
        *,
        allowed_extensions: Optional[Sequence[str]] = None,
        update_snapshot: bool = False,
    ) -> List[str]:
        """
        Varre todos os blobs sob um prefixo e retorna a lista dos que mudaram
        segundo as regras de comparação de metadados.

        Args:
            prefix: Ex.: "enriched/parquet/fundos" (com ou sem barra final).
            allowed_extensions: Ex.: [".parquet", ".xlsx"] para filtrar por sufixo.
            update_snapshot: Se True, atualiza o snapshot para os que mudaram.

        Returns:
            Lista de paths de blobs que mudaram.
        """
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        extensions = tuple(e.lower() for e in (allowed_extensions or []))
        changed_paths: List[str] = []

        for blob_item in self._container_client.list_blobs(name_starts_with=prefix):
            name = blob_item.name
            if name.endswith("/"):
                continue
            if extensions and not name.lower().endswith(extensions):
                continue

            previous = self._get_snapshot_metadata(name)
            current = BlobMetadata.from_blob_properties(blob_item)

            if previous is None:
                has_changed = self._treat_missing_as_changed
            else:
                has_changed = (
                    current.etag != previous.etag
                    or current.last_modified_utc != previous.last_modified_utc
                    or current.size_bytes != previous.size_bytes
                )

            if has_changed:
                changed_paths.append(name)
                if update_snapshot:
                    self._snapshot[name] = current.to_dict()

        if update_snapshot and changed_paths:
            self._save_snapshot()

        return changed_paths



