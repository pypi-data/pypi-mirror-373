import io, os
from pathlib import PurePosixPath
from datetime import timezone
import pandas as pd
import pyarrow as pa, pyarrow.parquet as pq
import pickle
import re

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

from ..dataframe import read_bytes


class BlobParquetClient:
    """Leitura/gravacao de Parquet em Azure Blob – stateless & reutilizável."""

    def __init__(self, container: str = "luxorasap", adls_connection_string: str = None):
        if adls_connection_string is None:
            adls_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
        self._svc = BlobServiceClient.from_connection_string(adls_connection_string)
        self._container = container

    # ---------- API pública ----------
    def read_df(self, blob_path: str) -> (pd.DataFrame, bool):
        buf = io.BytesIO()
        try:
            self._blob(blob_path).download_blob().readinto(buf)
            return (
                read_bytes(buf.getvalue(), filename=PurePosixPath(blob_path).name),
                True,
            )
        except Exception:
            return None, False
            

    def write_df(self, df, blob_path: str):
        
        blob = self._blob(blob_path)
        table = pa.Table.from_pandas(df)
        buf = io.BytesIO()
        pq.write_table(table, buf)
        buf.seek(0)
        blob.upload_blob(buf, overwrite=True)
            
        
    def get_df_update_time(self, blob_path: str) -> float:
        try:
            properties = self._blob(blob_path).get_blob_properties()
            return properties['last_modified'].replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            return 0.0
    
    
    def exists_df(self, blob_path: str) -> bool:
        try:
            self._blob(blob_path).get_blob_properties()
            return True
        except Exception:
            return False


    def list_blob_files(self, blob_path: str, ends_with: str = None) -> list:
        """
        Lista os arquivos em um diretório do blob storage.

        Args:
            blob_path (str): O caminho do diretório no blob storage.
            ends_with (str, optional): Filtra os arquivos que terminam com esta string.(Ex.: '.parquet')

        Returns:
            list: Uma lista de nomes de blob.
            
        """
        try:
            container_client = self._svc.get_container_client(self._container)
            blob_list = container_client.list_blobs(name_starts_with=blob_path)
            if ends_with:
                return [blob.name for blob in blob_list if blob.name.endswith(ends_with)]
            return [blob.name for blob in blob_list]
        except Exception:
            return []
            

    def table_exists(self, table_path: str) -> bool:
        """
            Checa se uma tabela existe no blob storage.
        """
        return self.exists_df(table_path)
    
    
    # ---------- interno --------------
    def _blob(self, path: str):
        path = str(PurePosixPath(path))
        return self._svc.get_blob_client(self._container, path)
    

class BlobPickleClient:
    def __init__(self, *, adls_connection_string: str = None, container: str = "luxorasap"):
        if adls_connection_string is None:
            adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            
        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
        
        self._svc = BlobServiceClient.from_connection_string(adls_connection_string)
        self._container = self._svc.get_container_client(container)


    def write_pickle(self, obj, blob_name: str):
        """Salva objeto Python (ex: DataFrame) como pickle no blob"""
        buf = io.BytesIO()
        pickle.dump(obj, buf)
        buf.seek(0)
        self._container.upload_blob(name=blob_name, data=buf, overwrite=True)


    def read_pickle(self, blob_name: str):
        """Lê pickle do blob e retorna objeto Python"""
        downloader = self._container.download_blob(blob_name)
        buf = io.BytesIO(downloader.readall())
        return pickle.load(buf)


    def exists(self, blob_name: str) -> bool:
        return self._container.get_blob_client(blob_name).exists()
    
    

class BlobExcelClient:
    def __init__(self, *, adls_connection_string: str = None, container: str = "luxorasap"):
        if adls_connection_string is None:
            adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if adls_connection_string is None:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
            
        self._svc = BlobServiceClient.from_connection_string(adls_connection_string)
        self._container = self._svc.get_container_client(container)


    def write_excel(self, df: pd.DataFrame, blob_name: str, **kwargs):
        """
        Salva um DataFrame como arquivo Excel no blob.

        Args:
            df (pd.DataFrame): DataFrame a ser salvo
            blob_name (str): caminho/nome do blob (ex: "reports/test.xlsx")
            **kwargs: argumentos extras para `DataFrame.to_excel`
        """
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl", **kwargs)
        buf.seek(0)
        self._container.upload_blob(name=blob_name, data=buf, overwrite=True)


    def write_excel_multiple_sheets(
        self,
        sheets: dict[str, pd.DataFrame],
        blob_name: str,
        *,
        index: bool = False,
        engine: str = "openpyxl",
        **to_excel_kwargs,
    ) -> None:
        """
        Salva várias abas de uma planilha Excel no blob, a partir de um dicionário
        {nome_aba: DataFrame}.

        Args:
            sheets: Mapa de nome da aba -> DataFrame.
            blob_name: Caminho/nome do blob (ex.: "reports/minha_planilha.xlsx").
            index: Se True, escreve o índice dos DataFrames.
            engine: Engine do pandas.ExcelWriter (default "openpyxl").
            **to_excel_kwargs: repassado a `DataFrame.to_excel` (ex.: na_format, float_format).
        """

        def _sanitize_sheet_name(name: str) -> str:
            # Excel limita a 31 chars e proíbe alguns caracteres
            s = str(name)[:31]
            for ch, repl in {":": "_", "/": "_", "\\": "_", "?": "_", "*": "_", "[": "(", "]": ")"}.items():
                s = s.replace(ch, repl)
            return s

        if not isinstance(sheets, dict) or not sheets:
            raise ValueError("`sheets` deve ser um dicionário não vazio 'aba': 'DataFrame'.")

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine=engine) as writer:
            for sheet_name, df in sheets.items():
                sanitized = _sanitize_sheet_name(sheet_name)
                if not isinstance(df, pd.DataFrame):
                    # tenta converter objetos "tabelares" em DataFrame
                    df = pd.DataFrame(df)
                df.to_excel(writer, sheet_name=sanitized, index=index, **to_excel_kwargs)

        buf.seek(0)
        self._container.upload_blob(name=blob_name, data=buf, overwrite=True)



    def read_excel(self, blob_name: str, **kwargs) -> pd.DataFrame:
        """
        Lê um arquivo Excel do blob e retorna um DataFrame.

        Args:
            blob_name (str): caminho/nome do blob (ex: "reports/test.xlsx")
            **kwargs: argumentos extras para `pd.read_excel`

        Returns:
            pd.DataFrame
        """
        downloader = self._container.download_blob(blob_name)
        buf = io.BytesIO(downloader.readall())
        return pd.read_excel(buf, engine="openpyxl", **kwargs)

    def exists(self, blob_name: str) -> bool:
        return self._container.get_blob_client(blob_name).exists()
    
 
    
def list_blob_files(blob_path: str, container="luxorasap", ends_with: str = None, adls_connection_string: str = None) -> list:
    """
    Lista os arquivos em um diretório do blob storage.

    Args:
        blob_path (str): O caminho do diretório no blob storage.
        ends_with (str, optional): Filtra os arquivos que terminam com esta string.(Ex.: '.parquet')

    Returns:
        list: Uma lista de nomes de blob.
        
    """
    
    if adls_connection_string is None:
        adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if adls_connection_string is None:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
    
    try:
        svc  = BlobServiceClient.from_connection_string(adls_connection_string)
        container_client = svc.get_container_client(container)
        blob_list = container_client.list_blobs(name_starts_with=blob_path)
        if ends_with:
            return [blob.name for blob in blob_list if blob.name.endswith(ends_with)]
        return [blob.name for blob in blob_list]
    except Exception:
        return []
        

def delete_blob(
    blob_name: str,
    *,
    adls_connection_string: str | None = None,
    container: str = "luxorasap",
    include_snapshots: bool = False,
) -> None:
    """
    Exclui com segurança APENAS um arquivo (blob) exato do Azure Blob Storage.

    Regras de segurança:
      - Recusa nomes que terminem com "/" (prefixos de diretório virtual).
      - Recusa curingas/shell globs (*, ?, []), para evitar exclusões indevidas.
      - Verifica a existência do blob exato antes de remover.

    Args:
        blob_name: Caminho EXATO do blob (ex.: "enriched/parquet/tabela.parquet").
        adls_connection_string: Se None, lê de AZURE_STORAGE_CONNECTION_STRING.
        container: Nome do container.
        include_snapshots: Se True, apaga snapshots vinculados ao blob.

    Raises:
        ValueError: Se o nome parecer um diretório/prefixo ou contiver curingas.
        FileNotFoundError: Se o blob exato não existir.
        RuntimeError: Se a conexão com o Azure não estiver configurada.
    """
    if adls_connection_string is None:
        adls_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if adls_connection_string is None:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not set")
    
    # 1) Bloqueios contra “diretórios” e curingas
    if blob_name.endswith("/"):
        raise ValueError("Nome termina com '/': recusa exclusão de diretórios/prefixos.")
    if re.search(r"[\*\?\[\]]", blob_name):
        raise ValueError("Curingas encontrados no nome do blob. Informe um arquivo exato.")

    svc = BlobServiceClient.from_connection_string(adls_connection_string)
    container_client = svc.get_container_client(container)
    blob_client = container_client.get_blob_client(blob_name)

    # 2) Checa existência do blob exato
    try:
        blob_client.get_blob_properties()
    except ResourceNotFoundError:
        raise FileNotFoundError(f"Blob não encontrado: {blob_name}")

    # 3) Exclui apenas o alvo exato
    delete_kwargs = {}
    if include_snapshots:
        delete_kwargs["delete_snapshots"] = "include"

    blob_client.delete_blob(**delete_kwargs)

    