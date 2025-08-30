import pandas as pd
import datetime as dt
import time
import io
import sys, os

from loguru import logger
from pathlib import Path

from azure.storage.blob import BlobServiceClient
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv
load_dotenv()

from luxorasap.datareader import LuxorQuery
from luxorasap.utils.dataframe import transforms
from luxorasap.ingest import save_table
from luxorasap.utils.tools.excel import close_excel_worksheet

import warnings
warnings.warn(
    "luxorasap.ingest.legacy_local.dataloader é legado; "
    "utilize luxorasap.ingest.cloud em novas rotinas.",
    DeprecationWarning, stacklevel=2
)



class DataLoader:

    def __init__(self, luxorDB_directory = None):
        """Fornece uma forma padronizada de carregar tabelas para a luxorDB.
            1. Possui metodos para carregar tabelas que já estao carregadas na memória
                - Sao os metodos que possuem 'table' no nome
            2. Possui metodos para carregar arquivos de excel, com todas as suas abas
                Inclui metodo para checagem de alteracao de versao do arquivo
                - Sao os metodos que possuem 'file' no nome
        Args:
            luxorDB_directory (pathlib.Path, optional): Caminho completo ate o diretorio de destino dos dados.
        """
        self.luxorDB_directory = luxorDB_directory

        if self.luxorDB_directory is None:
            self.luxorDB_directory = Path(__file__).absolute().parent/"LuxorDB"/"tables"

        self.tracked_files = {}
        self.tracked_tables = {}
    

    def add_file_tracker(self, tracked_file_path, filetype="excel", sheet_names={}, 
            excel_size_limit = None,index=False, index_name="index", normalize_columns=False):
        """ Adiciona arquivo na lista para checar por alteracao
        Args:
            tracked_file_path (pathlib.Path): caminho completo ate o arquivo,
                    incluindo nome do arquivo e extensão.
            sheet_names (dict, optional): Caso seja uma planilha com varias abas, mapear
                    aqui o nome da aba para o nome do arquivo de saida desejado.
        """
        if tracked_file_path not in self.tracked_files:
            self.tracked_files[tracked_file_path] = {
                    "last_mtime" : dt.datetime.timestamp(dt.datetime(2000,1,1)),
                    "filetype" : filetype, "sheet_names": sheet_names,
                    "excel_size_limit" : excel_size_limit,
                    "index" : index,
                    "index_name" : index_name,
                    "normalize_columns" : normalize_columns,
                }


    def add_table_tracker(self, table_name:str):
        """ Adiciona tabela na lista para controle de alteracao."""

        if table_name not in self.tracked_tables:
            self.tracked_tables[table_name] = dt.datetime.timestamp(dt.datetime(2000,1,1))


    def remove_file_tracker(self, tracked_file_path):

        if tracked_file_path in self.tracked_files:
            del self.tracked_files[tracked_file_path]
    

    def remove_table_tracker(self, table_name:str):

        if table_name in self.tracked_tables:
            del self.tracked_tables[table_name]


    def is_file_modified(self, tracked_file_path: Path) -> {bool, float}:
        """ Checa se o arquivo foi modificado desde a ultima leitura.
        Returns:
            tuple(bool, float): (foi modificado?, timestamp da ultima modificacao)
        """

        file_data = self.tracked_files[tracked_file_path]
        
        last_saved_time = file_data["last_mtime"]
        file_last_update = tracked_file_path.stat().st_mtime
        return file_last_update > last_saved_time, file_last_update
    

    def set_file_modified_time(self, tracked_file_path, file_mtime):

        self.tracked_files[tracked_file_path]["last_mtime"] = file_mtime
        

    def load_file_if_modified(self, tracked_file_path, export_to_blob=False, blob_directory='enriched/parquet', trials=25):
        """Carrega arquivo no caminho indicado, carregando na base de dados caso modificado.
        Args:
            tracked_file_path (pathlib.Path): caminho ate o arquivo(cadastro previamente por add_file_tracker)
            type_map (_type_, optional): _description_. Defaults to None.
            filetype (str, optional): _description_. Defaults to "excel".
        """
        file_data = self.tracked_files[tracked_file_path]
        
        last_saved_time = file_data["last_mtime"]
        filetype = file_data["filetype"]
        file_sheets = file_data["sheet_names"]

        file_last_update = tracked_file_path.stat().st_mtime

        if file_last_update > last_saved_time: # Houve alteracao no arquivo
            if filetype == "excel":
                file_sheets = None if len(file_sheets) == 0 else list(file_sheets.keys())

                # tables sera sempre um dicionario de tabelas
                tables = None
                t_counter = 1
                while trials - t_counter > 0:
                    try:
                        tables = pd.read_excel(tracked_file_path, sheet_name=file_sheets)
                        t_counter = trials # leitura concluida
                    except PermissionError:
                        
                        logger.error(f"Erro ao tentar ler arquivo '{tracked_file_path}.\nTentativa {t_counter} de {trials};'.\nSe estiver aberto feche.")
                        
                        t_counter += 1
                        if trials - t_counter == 1:
                            close_excel_worksheet(tracked_file_path.name, save=True)
                        time.sleep(10)

                for sheet_name, table_data in tables.items():

                    table_name = sheet_name if file_sheets is None else file_data["sheet_names"][sheet_name]

                    if table_name == "trades":
                        table_data["ID"] = table_data.index

                    #self.__export_table(table_name, table_data, index=file_data["index"], index_name=file_data["index_name"],
                    #                        normalize_columns=file_data["normalize_columns"], export_to_blob=export_to_blob,
                    #                        blob_directory=blob_directory)
                    save_table(table_name, table_data, index=file_data["index"], index_name=file_data["index_name"],
                               normalize_columns=file_data["normalize_columns"], directory=blob_directory, override=True)
                    
                self.tracked_files[tracked_file_path]["last_mtime"] = file_last_update
            
        
    def load_table_if_modified(self, table_name, table_data, last_update, index=False, index_name="index", normalize_columns=False,
                               do_not_load_excel=False, export_to_blob=False, blob_directory='enriched/parquet',
                               is_data_in_bytes=False, bytes_extension=".xlsx"):
        """
        Args:
            table_name (str): nome da tabela (sera o mesmo do arquivo a ser salvo)
            table_data (pd.DataFrame): tabela de dados
            last_update (timestamp): timestamp da ultima edicao feita na tabela
        """

        if table_name not in self.tracked_tables:
            self.add_table_tracker(table_name)


        last_update_time = self.tracked_tables[table_name]
        if last_update > last_update_time:
            
            self.tracked_tables[table_name] = last_update
            self.__export_table(table_name, table_data, index=index, index_name=index_name, normalize_columns=normalize_columns,
                                do_not_load_excel=do_not_load_excel, export_to_blob=export_to_blob, blob_directory=blob_directory,
                                is_data_in_bytes=is_data_in_bytes, bytes_extension=bytes_extension)


    def scan_files(self, export_to_blob=False, blob_directory='enriched/parquet'):
        """
            Para todos os arquivos cadastrados, vai buscar e carregar quando houver
            arquivo mais recente.
        """

        for file in self.tracked_files:
            
            self.load_file_if_modified(file, export_to_blob=export_to_blob, blob_directory=blob_directory)


    #def __load_bytes(self, content: bytes, extension=".xlsx") -> pd.DataFrame:
    #    if extension == ".xlsx" or extension == "xlsx" or extension == "xls":
    #        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    #    
    #        return df
#
    #    raise ValueError(f'Extension {extension} not supported')
    
    def __load_bytes(self, content: bytes, extension: str) -> pd.DataFrame:
        extension = extension.lower()

        if extension in [".xlsx", ".xls", "xlsx", "xls"]:
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
            return df
        
        if extension == ".csv":
            try:
                return pd.read_csv(io.BytesIO(content), encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(io.BytesIO(content), encoding="latin1")

        if extension == ".parquet":
            df = pd.read_parquet(io.BytesIO(content))
            return df

        raise ValueError(f'Extension {extension} not supported')


    def __export_table(self, table_name, table_data, index=False, index_name="index", normalize_columns=False,
                       do_not_load_excel=False, export_to_blob=False, blob_directory='enriched/parquet',
                       is_data_in_bytes=False, bytes_extension=".xlsx"):
        
        dest_directory = self.luxorDB_directory
        #TODO -> formatar para index=False
        # Salvando em formato excel
        attempts = 10
        count_attempt = 0

        if is_data_in_bytes:
            table_data = self.__load_bytes(table_data, extension=bytes_extension)

        # Se o index tiver dados, vamos trata-los para virar uma coluna
        if index:
            # Tratando o nome do index, caso seja necessario transformar em coluna
            prev_index = table_data.index.name
            if prev_index is not None and index_name == "index":
                index_name = prev_index
            table_data.index.name = index_name

            table_data = table_data.reset_index()


        if normalize_columns:
            table_data = transforms.persist_column_formatting(table_data)

        if not do_not_load_excel:
            while count_attempt < attempts:
                count_attempt += 1
                try:
                    if len(table_data) > 1_000_000:
                        table_data = table_data.tail(1_000_000)
                    table_data.to_excel(dest_directory/f"{table_name}.xlsx", index=False)
                    count_attempt = attempts # sair do loop
                    
                except PermissionError:
                    logger.error(f"Erro ao tentar salvar arquivo {table_name}. Feche o arquivo. Tentativa {count_attempt} de {attempts}")
                    time.sleep(10 + count_attempt * 5)

        # Salvando em csv 
        # -> Salvar em csv foi descontinuado por falta de uso.
        #table_data.to_csv(dest_directory/"csv"/f"{table_name}.csv", sep=";", index=False)

        # Salvando em parquet (tudo como string... dtypes deverao ser atribuidos na leitura)
        table_data = table_data.astype(str)
        table_data.to_parquet(dest_directory/"parquet"/f"{table_name}.parquet", engine="pyarrow", index=False)

        if export_to_blob:
            # Definindo o Container e o Blob Name
            container_name = "luxorasap"
            blob_name = f"{blob_directory}/{table_name}.parquet"  #
            
            # Conversão para parquet em memória (sem precisar salvar local)
            table = pa.Table.from_pandas(table_data)
            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)  # Reseta o ponteiro para o início do buffer

            # Conectando ao Blob Storage
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)

            # Criando um Blob Client
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(parquet_buffer, overwrite=True)
        
