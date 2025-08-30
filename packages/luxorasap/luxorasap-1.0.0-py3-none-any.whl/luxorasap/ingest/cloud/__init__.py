"""Camada moderna de ingestão: grava / incrementa tabelas em ADLS (Parquet)."""

import pandas as pd
import datetime as dt
import numpy as np

from luxorasap.utils.storage import BlobParquetClient, BlobExcelClient, BlobPickleClient
from luxorasap.utils.dataframe import prep_for_save, astype_str_inplace
from luxorasap.datareader import LuxorQuery
from luxorasap.utils.storage import BlobChangeWatcher



__all__ = ["save_table", "incremental_load"]

_client = BlobParquetClient()   # instância única para o módulo


# ────────────────────────────────────────────────────────────────
def save_table(
    table_name: str,
    df,
    *,
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
    override=False,
    format='parquet'
):
    """Salva DataFrame como arquivo Parquet no ADLS.
         Args:
        table_name (str): Nome da tabela (será o nome do arquivo).
        df (pd.DataFrame): DataFrame a ser salvo.
        index (bool, optional): Se True, salva o índice do DataFrame. Defaults to False.
        index_name (str, optional): Nome da coluna de índice, se `index` for True. Defaults to "index".
        normalize_columns (bool, optional): Se True, normaliza nomes de colunas. Defaults to True.
        directory (str, optional): Subdiretório no container 'luxorasap'. Defaults to "enriched/parquet".
        override (bool, optional): Se True, sobrescreve a tabela existente. Defaults to False.
        format (str): Formato de saída ('parquet', 'excel', 'excel_multiple_sheets', 'pickle'). Defaults to 'parquet'.
        """
    
    # Se df for um pandas dataframe
    if isinstance(df, pd.DataFrame):
        if 'Last_Updated' not in df.columns:
            df['Last_Updated'] = dt.datetime.now()
        else:
            # usando numpy, vamos substituir NaN ou 'nan' pela data e hora de agora
            df["Last_Updated"] = np.where(((df["Last_Updated"].isna()) | (df["Last_Updated"] == 'nan')),
                                        dt.datetime.now(),
                                        df["Last_Updated"]
                                        )    
    
        if override == False:
            lq = LuxorQuery()
            if lq.table_exists(table_name):
                return
    
        df = prep_for_save(df, index=index, index_name=index_name, normalize=normalize_columns)
    
    if format == 'parquet':
        #_client.write_df(df.astype(str), f"{directory}/{table_name}.parquet")
        astype_str_inplace(df)
        _client.write_df(df, f"{directory}/{table_name}.parquet")
    
    elif format == 'excel':

        _client_excel = BlobExcelClient()
        if index:
            df = df.reset_index().rename(columns={"index": index_name})
        _client_excel.write_excel(df, f"{directory}/{table_name}.xlsx")
        
    elif format == 'excel_multiple_sheets':
        _client_excel = BlobExcelClient()
        # df neste caso é um dicionário de DataFrames
        _client_excel.write_excel_multiple_sheets(df, f"{directory}/{table_name}.xlsx")
    
    elif format == 'pickle':
        _client_pickle = BlobPickleClient()
        _client_pickle.write_pickle(df, f"{directory}/{table_name}.pkl")
    
    else:
        raise ValueError(f"Formato '{format}' não suportado. Use 'parquet', 'excel' ou 'pickle'.")



def incremental_load(
    lq: LuxorQuery,
    table_name: str,
    df,
    *,
    increment_column: str = "Date",
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
    unique_columns: list = None
):
    """Concatena novos dados aos existentes, cortando duplicados pela data."""
    df["Last_Updated"] = dt.datetime.now()
    
    if lq.table_exists(table_name):
        prev = lq.get_table(table_name, drop_last_updated_columns=False)
        if increment_column is not None:
            if increment_column not in df.columns:
                raise ValueError(f"Coluna de incremento '{increment_column}' não existe no DataFrame.")
            cutoff = df[increment_column].max()
            prev = prev.query(f"{increment_column} < @cutoff")
        df = pd.concat([prev, df], ignore_index=True)
        # remover duplicados
    
    if unique_columns is not None:
        df = df.drop_duplicates(subset=unique_columns, keep='last')

    save_table(
        table_name,
        df,
        index=index,
        index_name=index_name,
        normalize_columns=normalize_columns,
        directory=directory,
        override=True
    )
    
    
class TableDataLoader:

    def __init__(self, update_func: callable, kwargs: dict = {}, adls_connection_string: str = None ):
        """
        Controla o carregamento de tabelas baseado em mudanças de arquivos no ADLS.
        Args:
            update_func (callable): Funcao que sera chamada para atualizar a tabela.
            kwargs (dict): Dicionario com os argumentos para a funcao de update.
            luxordb_path (Path, optional): Caminho para o diretorio raiz do luxorDB.
                Defaults to None.
        """
        self.tracked_files = {}
        self.adls_connection_string = adls_connection_string
        self.update_func = update_func
        self.kwargs = kwargs

        
    def add_load_trigger(self, directory: str, trigger_name: str):
        """ Adiciona tabela na lista para controle de alteracao.
            O load sera disparado quando essa tabela for atualizada.
        Args:
            table_path (Path): Path para a tabela que ira disparar a atualizacao.
        """
        
        blob_watcher = BlobChangeWatcher(watcher_id=trigger_name, 
                                         adls_connection_string=self.adls_connection_string)
        self.tracked_files[directory] = blob_watcher

    
    def table_load_triggered(self, trigger_mode="any") -> bool:
        """Verifica se alguma das trigger tables foi atualizada.
        trigger_mode: "any" ou "all".
        """

        if trigger_mode == "any":
            load_triggered = False
            # Verificando se alguma das tabelas foi atualizada
            for trigger_path in self.tracked_files.keys():
                blob_watcher = self.tracked_files[trigger_path]
                file_updated, _, _ = blob_watcher.has_changed(blob_path = trigger_path,
                                                                        update_snapshot=True,
                                                                        treat_missing_as_changed=True
                                                                        )
                if file_updated:
                    load_triggered = True #load_triggered | True
        
            return load_triggered
        
        if trigger_mode == "all":
            load_triggered = True
            # Verificando se alguma das tabelas foi atualizada
            for trigger_path in self.tracked_files.keys():
                blob_watcher = self.tracked_files[trigger_path]
                file_updated, _, _ = blob_watcher.has_changed(blob_path = trigger_path,
                                                                        update_snapshot=False,
                                                                        treat_missing_as_changed=True
                                                                        )
                if not file_updated:
                    load_triggered = False #load_triggered | True
            if load_triggered:
                # Fazer do estado dos snapshots
                for trigger_path in self.tracked_files.keys():
                    blob_watcher = self.tracked_files[trigger_path]
                    blob_watcher.update_snapshot(trigger_path)
            return load_triggered
            


    def load_table(self):
        """Carrega a tabela via funcao de atualização.
        Args:
            kwargs (dict): Dicionario com os argumentos para a funcao de update.
        """
        self.update_func(**self.kwargs)