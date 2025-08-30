# Imports
import pandas as pd
import datetime as dt
from datetime import timezone
import logging
import os, sys
import time
import numpy as np
from scipy.optimize import newton
import io
from dotenv import load_dotenv

import pyarrow as pa
import pyarrow.parquet as pq

from luxorasap.utils.storage import BlobParquetClient
load_dotenv()

# Nao fazer import do ingest, risco de impor circular.


#ADLS_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

#@logger.catch
class LuxorQuery:

    # Criando construtor com docstring detalhada
    def __init__(self, blob_directory='enriched/parquet', adls_connection_string:str=None, 
                 container_name="luxorasap"):
        """
        Classe para consulta de dados da Luxor.
        Args:
            blob_directory (str, optional): Diretório no blob onde estão as tabelas. Defaults to 'enriched/parquet'.
            adls_connection_string (str, optional): String de conexão com o ADLS. Se None, usa variável de ambiente. Defaults to None.
            container_name (str, optional): Nome do container no blob. Defaults to "luxorasap".
        """
            
        self.blob_client = BlobParquetClient(adls_connection_string=adls_connection_string,
                                container=container_name)
        self.blob_directory = blob_directory

        
        self.modified_tables = []
        
        
        #if tables_path is None:
        #    self.tables_path = self.__set_tables_path()

        self.tables_in_use = {}
        self.asset_last_prices = {}
        self.price_cache = {}  # otimizacao da consulta de preco
        self.price_tables_loaded = {}


        self.lipi_manga_incorp_date = dt.date(2022,12,9)
        

        self.update() # Nessa 1° exec. vai inicializar os dicionarios acima


    def __is_table_modified(self, table_name):
        """ Retorna 'True' ou 'False' informando se a tabela informada em 'table_name' foi criada ou modificada.

        Args:
            table_name (str): nome tabela
            table_path (str): caminho ate a tabela no blob
        Returns:
            bool: True se foi criada ou modificada
        """
        
        if table_name not in self.tables_in_use:
            return True
        
        try:
            file_path = self.tables_in_use[table_name]["table_path"]
            file_last_update = self.blob_client.get_df_update_time(file_path)#self.__get_blob_update_time(table_name)
            return file_last_update > self.tables_in_use[table_name]["update_time"]

        except:
            logging.info(f"Arquivo <{file_path}> não encontrado.")

        return False
         
    
    def __get_tickers_bbg(self):
        # Deprecated. 
        # Criado apenas para manter compatibilidade
        logging.info("Acesso direto a tabela 'bbg_ticker' sera descontinuado.\nAo inves disso, pegue os valores unicos de asset[Ticker_BBG]")
        return pd.DataFrame(self.get_table("assets")["Ticker_BBG"].unique())


    def table_exists(self, table_name, blob_directory=None):
        # Checa no ADLS se existe alguma tabela com o nome informado
        
        if blob_directory is None:
            blob_directory = self.blob_directory
        
        table_path = f"{blob_directory}/{table_name}.parquet"
            
        return self.blob_client.table_exists(table_path)


    def list_tables(self):
        """Lista todas as tabelas disponiveis no blob"""
        tables = self.blob_client.list_blob_files(self.blob_directory, ends_with=".parquet")
        tables = [os.path.basename(t).replace(".parquet","") for t in tables]
        return tables
    

    def get_table(self, table_name, index=False, index_name="index", dtypes_override={}, force_reload=False,
                  drop_last_updated_columns=True, auto_convert_mapped_types=True):
        """
            Retorna uma copia do DataFrame do 'table_name' correspondente. Se não estiver disponivel,
            retorna None.
            
            table_name: 
                'px_last'              - Último preco dos ativos\n
                'trades'               - Historico de boletas dos trades da Luxor\n
                'assets'               - Tabela de ativos validos\n
                'hist_px_last'         - Preço histórico dos ativos desde 1990\n
                'hist_vc_px_last'      - Preço histórico dos VCs\n
                'hist_non_bbg_px_last' - Preço histórico de ativos sem preco no bbg (fidc trybe, spx hawker)\n
                '[NOME_FUNDO]_quotas   - Cotas historicas do fundo (fund_a, fund_b, hmx, ...\n
                'hist_us_cash'         - Historico de caixas dos fundos (us apenas)\n
                'bbg_tickers'          - Ticker bbg de todos os tickers cadastrados\n
                'bdr_sizes'            - Tabela com o ultimo peso de cada bdr\n
                'hist_swap'            - Tabela historica dos swaps\n
                'hist_positions'       - Historico de posicoes dos fundos\n
                'hist_positions_by_bank- Posicoes por banco\n
                'cash_movements'       - Historico de movimentacoes com data de liquidacao\n
                'holidays'             - Tabela de feriados das bolsas\n
                'daily_pnl'            - Tabela de PnL diario\n
                'custom_funds_quotas'  - Cotas dos fundos customizados(luxor equities, non-equities, etc)\n
            
            dtypes_override: dict : set - Dicionario com os tipos de dados das colunas devem ser sobrescritos.
                Deve possuir as chaves 'float', 'date', 'bool' e 'str_nan_format'(troca 'nan' por pd.NA)
                    Para cada chave, colocar um Set com os nomes das colunas que receberao o cast.
            
        """
        table_name = table_name.lower().replace(" ", "_")
        if table_name == 'bbg_tickers': return self.__get_tickers_bbg() # DEPRECATED TODO: remover apos testes

        if (table_name in self.tables_in_use) and not force_reload:
            return self.tables_in_use[table_name]["table_data"]

        
        table_data = self.__load_table(table_name, index=index, index_name=index_name, dtypes_override=dtypes_override,
                                       auto_convert_mapped_types=auto_convert_mapped_types,
                                       drop_last_updated_columns=drop_last_updated_columns)
        
        return table_data



    def __load_table(self, table_name, index=False, index_name="index", dtypes_override={}, auto_convert_mapped_types=True,
                     drop_last_updated_columns=True):
        def __load_parquet(table_name):
            table_path = f"{self.blob_directory}/{table_name}.parquet"#self.tables_path/"parquet"/f"{table_name}.parquet"
            
            try:
                #update_time = os.path.getmtime(table_path)
                table_data = None
                # Primeiro, vamos tentar ler do blob
                table_data, blob_read_success = self.blob_client.read_df(table_path)#__read_blob_parquet(table_name)
        
                if not blob_read_success:
                    logging.info(f"Não foi possível carregar a tabela '{table_name}' do blob.")
                    #print("--> Onedrive fallback.")
                    #table_data = pd.read_parquet(table_path,engine="fastparquet")
                update_time = self.blob_client.get_df_update_time(table_path)
                
                assert(table_data is not None)
                
                if not auto_convert_mapped_types:
                    return table_data, table_path, update_time
                
                table_columns = set(table_data.columns)
                
                float_dtypes = {"Last_Price", "Price", "px_last", "Quota", "#", "Avg_price", "Variation", "Variation_tot",
                                "%_MoM", "PL", "AUM", "%_pl", "Market_Value", "P&L_MoM", "Debt", "Kd", "P&L_YTD", "Return_Multiplier",
                                "Weight", "%_YTD", "Net_Debt/Ebitda", "adr_adr_per_sh", "Volume", "Total","Liquidity_Rule",
                                "Daily_Return", "Amount", "Adjust", "Year", "Daily_Adm_Fee", "Timestamp",
                                "Pnl", "Attribution"}
                if 'float' in dtypes_override:
                    float_dtypes = float_dtypes.union(dtypes_override['float'])

                date_dtypes = {"Date", "last_update_dt", "Query_Time", "update_time", "Update_Time",
                               "Settlement Date", "Today"}
                if 'date' in dtypes_override:
                    date_dtypes = date_dtypes.union(dtypes_override['date'])

                bool_dtypes = {"Ignore Flag", "Disable BDP", "Hist_Price", "Historical_Data"}
                if 'bool' in dtypes_override:
                    bool_dtypes = bool_dtypes.union(dtypes_override['bool'])

                str_nan_format = {"Ticker_BBG"}
                if 'str_nan_format' in dtypes_override:
                    str_nan_format = str_nan_format.union(dtypes_override['str_nan_format'])
                
                if table_name != "last_all_flds":
                    try:
                        for col in table_columns.intersection(float_dtypes):
                            table_data[col] = table_data[col].astype(float)
                    except :
                        logging.info(f"Ao carregar tabela '{table_name}', nao foi possivel converter dados da coluna {col} para float.")
                        #logging.info(f"Colunas com erro: {table_columns.intersection(float_dtypes)}")
                        #logging.info(f"Colunas disponiveis: {table_columns}")
                        #print(table_data.dtypes)
                        
                        raise ValueError(f"Erro ao converter colunas para float na tabela '{table_name}'.")
                    
                if table_name == "hist_risk_metrics":
                    try:
                        cols_to_format = list(set(table_data.columns) - {"Date", "Fund"})
                        table_data[cols_to_format] = table_data[cols_to_format].astype(float)
                    except ValueError:
                        logging.info("Ao carregar tabela 'hist_px_last', nao foi possivel converter dados para float.")

                for col in table_columns.intersection(date_dtypes):
                    try:
                        table_data[col] = pd.to_datetime(table_data[col], format="mixed")

                    except ValueError:
                        table_data[col] = table_data[col].apply(lambda x: pd.to_datetime(x))
                
                for col in table_columns.intersection(bool_dtypes):
                    try:
                        table_data[col] = (table_data[col].str.lower()
                                                        .replace("false", "").replace("falso", "")
                                                        .replace("0", "").replace("nan", "").astype(bool))
                    except Exception:
                        logging.info(f"Ao carregar tabela '{table_name}', nao foi possivel converter dados da coluna {col} para bool.")
                        raise ValueError(f"Erro ao converter coluna {col} para bool na tabela '{table_name}'.")
                                    
                for col in table_columns.intersection(str_nan_format):
                    table_data[col] = table_data[col].replace("<NA>", pd.NA).replace("nan", pd.NA).replace("", pd.NA)
                
                return table_data.copy(), table_path, update_time
            
            except Exception:
                logging.info(f"Nao foi possivel carregar a tabela <{table_name}>.")
                return None, None, None
        
        #def __load_csv(table_name):
        #    table_path = self.tables_path/"csv"/f"{table_name}.csv"
        #    
        #    try:
        #        update_time = os.path.getmtime(table_path)
        #        table_data = pd.read_csv(table_path, sep=";")
        #        return table_data.copy(), table_path, update_time
        #    except Exception:
        #        logging.info(f"Nao foi possivel carregar a tabela <{table_name}> no formato .csv")
        #        return None, None, None
        #
        #def __load_excel(table_name):
        #    try:
        #        table_path = self.tables_path/f"{table_name}.xlsx"
        #        update_time = os.path.getmtime(table_path)
        #        # Nao deixar crashar caso nao consiga ler do excel !
        #        table_data = pd.read_excel(table_path)
        #        logging.info(f"Tabela {table_name} carregada do arquivo em excel. Limite 1M de linhas.")
        #        return table_data.copy(), table_path, update_time
        #    except FileNotFoundError:
        #        return None, table_path, None       
        # Tentando carregar, do mais eficiente pro menos eficiente.
        table_data, table_path, update_time = __load_parquet(table_name)
        #if table_data is None: CSV DESCONTINUADO POR FALTA DE USO
        #    table_data, table_path, update_time = __load_csv(table_name)
        #if table_data is None:
        #    table_data, table_path, update_time = __load_excel(table_name)
        
        #assert(table_data is not None)
        if table_data is None:
            logging.info(f"Nao foi possivel carregar a tabela <{table_name}>.")
            return table_data
        
        if index:
            try: 
                table_data = table_data.set_index(index_name, drop=True)

            except Exception:
                logging.info(f"Nao foi possível setar a coluna {index_name} como index para a tabela {table_name}.")
        
        if (table_data is not None) and drop_last_updated_columns:
            if "Last_Updated" in table_data.columns:
                table_data = table_data.drop(columns=["Last_Updated"])

        #table_data = self.__persist_column_formatting(table_data)

        self.tables_in_use[table_name] = {"table_data" : table_data,
                                          "table_path" : table_path,
                                          "update_time" : update_time
                                          }
        return table_data


    def __load_table_group(self, table_keys):

        price_tables_loaded_flag = False

        for table_key in table_keys:

            index = table_key in ["px_last", "last_all_flds"]
            index_name = "Key" if table_key in ["px_last", "last_all_flds"] else None
            self.__load_table(table_key, index=index, index_name=index_name)

            if table_key == "px_last":
                self.asset_last_prices = self.get_table(table_key).to_dict("index")
                            
            elif table_key == "last_all_flds":
                self.last_all_flds = self.get_table(table_key).to_dict("index")

            elif table_key in ["hist_px_last", "hist_non_bbg_px_last", "hist_vc_px_last", "all_funds_quotas", "custom_funds_quotas", "custom_prices"]:
                price_tables_loaded_flag = True
                table = (self.get_table(table_key)
                            .rename(
                                columns={"Fund" : "Asset", "Quota" : "Last_Price", "Ticker" : "Asset",
                                            "Price" : "Last_Price"
                                            })[["Date","Asset","Last_Price"]]
                        )
                
                if table_key == 'hist_vc_px_last':
                    last_prices = table.groupby("Asset")["Last_Price"].last()
                    last_date_df = pd.DataFrame({"Date": [dt.datetime.now()] * len(last_prices)})
                    last_date_df["Asset"] = last_prices.index
                    last_date_df["Last_Price"] = last_prices.values
                    
                    table = (pd.concat([table, last_date_df]).sort_values(by="Date")
                                .set_index("Date").groupby("Asset")
                                .apply(lambda g: g[~g.index.duplicated(keep="first")].resample("D").ffill(),
                                       include_groups=False).reset_index()
                                )

                self.price_tables_loaded[table_key] = table
                
        if ('px_last' in table_keys) and ('hist_px_last' in self.tables_in_use):
            # Vamos pegar o px_last e colocar na tabela de precos historicos, atualizando ultima ocorrencia
            hist_prices = self.get_table("hist_px_last")
            hist_prices = self.__update_hist_px_last_intraday(hist_prices)
            self.price_tables_loaded["hist_px_last"] = hist_prices
            price_tables_loaded_flag = True

        if price_tables_loaded_flag: # Somente se a execucao alterou o estado de ´price_tables_loaded  
            self.hist_prices_table = pd.concat(self.price_tables_loaded.values()).dropna()


    def update(self, update_attempts_limit=8):
        """
            Atualiza todas as tabelas em uso.
        """

        update_attempts = 0
        update_success = False
        self.price_cache = {}  # -> reset da otimizacao da consulta de preco 

        while not update_success and (update_attempts < update_attempts_limit):
            try:
                update_attempts += 1
                for table_key in self.tables_in_use:
                    # Verificando se tabela foi criada ou modificada
                    if self.__is_table_modified(table_key):                        
                        self.__load_table_group([table_key])
                    

                update_success = True
                
            except PermissionError:
                hist_prices_tables = [] # desconsidera appends feitos no loop nao concluido
                logging.info("Não foi possível carregar as tabelas pois tem algum arquivo aberto.")
                logging.info(f"Tentativas de atualização: {update_attempts} de {update_attempts_limit}")
                time.sleep(30)

            except:
                logging.info("Não foi possivel carregar as tabelas.")
                logging.info(f"Tentativas de atualização: {update_attempts} de {update_attempts_limit}")
                time.sleep(5*update_attempts)

        if not update_success:
            logging.info("Nao foi possivel atualizar os dados. Execução finalizada.")

    
    def text_to_lowercase(self, t):
        """
        Converte todas as colunas de texto para lowercase
        Args:
            t (dt.DataFrame): pandas DataFrame
        Returns:
            dt.DataFrame
        """
        try:
            return t.map(lambda x: x.lower().strip() if isinstance(x, str) else x)
        except AttributeError:
            logging.info("Pendente de atualizacao para o python 3.12.2")
            return t.applymap(lambda x: x.lower().strip() if isinstance(x, str) else x)

    def get_px_update_time(self):
        """ Informa Horário da ultima atualizacao da base de precos.
        Returns:
            dt.datetime
        """
        time = self.get_table("px_last")["Query_Time"].max()
        return dt.time(time.hour, time.minute, time.second)
    

    def get_price_key(self, asset_key):
        """ Retorna a chave correta a ser usada para consultar o preco/rentabilidade do ativo."""
        
        asset = self.get_table("assets").query("Key == @asset_key").squeeze()
        
        if asset["Group"] in ["vc", "luxor"]:
            return asset["Ticker"]
        
        # Verificando se ha valor valido de ticker bbg
        if type(asset["Ticker_BBG"]) == type(""):

            return asset["Ticker_BBG"]
        # caso nao haja, sera usado o ticker
        return asset["Ticker"]
    

    def get_price(self, ticker, px_date=None, logger_level="trace", dr_adjusted=False,
        currency="local", usdbrl_ticker="bmfxclco curncy", asset_location="us"):
        """ Informa o preço do ativo. Quando px_date nao eh informado, retorna o
        preço mais recente.

        Args:
            ticker (str): identificador do ativo.
            px_date (dt.date, optional): Data de referencia.
            logger_level (str, optional): Defaults to "trace".

        Returns:
            float: preço do ativo.
        """
    
        if pd.isna(ticker): return None


        currency_factor = 1
        if currency != "local":
            try:
                if asset_location == "bz" and currency == "usd":
                    usdbrl = self.get_price(usdbrl_ticker, px_date=px_date)
                    currency_factor = 1/usdbrl
                elif asset_location == "us" and currency == "brl":
                    usdbrl = self.get_price(usdbrl_ticker, px_date=px_date)
                    currency_factor = usdbrl
            except ValueError:
                logging.info(f"Erro ao converter moeda para {currency} para o ticker '{ticker}'.")
                currency_factor = 1

        ticker = ticker.lower()
        
        # dados do usd cupom limpo comecam em abril de 2011. Antes disso vamos pergar usdbrl normalmente
        if (ticker == "bmfxclco curncy") and (px_date is not None) and (px_date < dt.date(2011,4,14) or (px_date is not None and px_date == dt.date.today())) :
            ticker = "usdbrl curncy"
        
        px_last_at_date = None
        
        cache_key = ticker + str(px_date) # chave unica do preco para essa data
        # se o preco foi consultado recentemente, podemos retorna-lo rapidamente.
        if cache_key in self.price_cache:
            return self.price_cache[cache_key] * currency_factor

        if (px_date is None) or (px_date>= dt.date.today()):
            # Nesse caso retornamos o mais recente utilizando o dicionario
            
            if "px_last" not in self.tables_in_use:
                self.__load_table_group(["px_last"])

            #if ticker in self.asset_last_prices.keys():
            try:
                px_last_at_date = self.asset_last_prices[ticker]["px_last"]
                self.price_cache[cache_key] = px_last_at_date
            except:
                price_1_tickers = ['fip mission 1.1', 'caixa', 'caixa us']
                if ticker in price_1_tickers :
                    px_last_at_date = 1
                    self.price_cache[cache_key] = px_last_at_date
                else:
                #if px_last_at_date is None:
                    if logger_level == "trace":
                        logging.info(f"Preço nao disponivel para o ticker '{ticker}'. Preço setado para 0.")
                    elif logger_level == "info":
                        logging.info(f"Preço nao disponivel para o ticker '{ticker}'. Preço setado para 0.")
                    else: # logger_level == "erro":
                        logging.info(f"Preço nao disponivel para o ticker '{ticker}'. Preço setado para 0.")
                    px_last_at_date = 0
            
            
            return px_last_at_date * currency_factor
        
        # Vamos olhar em cada tabela de precos procurando pelo ticker informado
        if not self.price_tables_loaded:
            self.__load_table_group(["hist_px_last", "hist_non_bbg_px_last", "hist_vc_px_last",
                                     "all_funds_quotas", "custom_funds_quotas", "custom_prices"])
            

        try:
            # Busca otimizada do preco pelo ativo e pela data informada
            #px_last_at_date = (self.hist_prices_table["Last_Price"]
            #                    .to_numpy()[(
            #                            (self.hist_prices_table["Date"].dt.date.to_numpy() <= px_date) 
            #                            & 
            #                            (self.hist_prices_table["Asset"].to_numpy() == ticker) 
            #                            )].item(-1)
            #                    )
            #return  px_last_at_date

            px_last_at_date = self.hist_prices_table.query("Date <= @px_date and Asset == @ticker")
            
            return px_last_at_date.tail(1)["Last_Price"].squeeze() * currency_factor if len(px_last_at_date) > 0 else 0

        except (IndexError , KeyError):
            # Nao achou o ativo em nenhuma das tabelas, retorna 0
            if logger_level == "trace":
                logging.info(f"Preço nao disponivel para o tikcker '{ticker}'. Preço setado para 0.")
            elif logger_level == "info":
                logging.info(f"Preço nao disponivel para o tikcker '{ticker}'. Preço setado para 0.")
            else: # logger_level == "erro":
                logging.info(f"Preço nao disponivel para o tikcker '{ticker}'. Preço setado para 0.")

            logging.info(f"Preço nao disponivel para o tikcker '{ticker}'. Preço setado para 0.")
            self.price_cache[cache_key] = px_last_at_date
            return 0
    

    def usdbrl_clean_coupon_fix(self, usdbrl_df):
        """ Corrige o problema do ticker bmfxclco curncy nao ter dados intraday.
            Usa a variacao intraday do usdbrl curncy
        Args:
            usdbrl_df (pd.DataFrame): dataframe com precos historicos do bmfxclco curncy
        """
        max_date = usdbrl_df["Date"].max().date()
        today = dt.date.today()
        if max_date < today:
            # vamos pegar a variacao do usdbrl curncy
            var_usdbrl = self.get_pct_change('usdbrl curncy', 
                                               recent_date=today,
                                               previous_date=max_date)
            # vamos pegar o last_price em max_date
            last_price = usdbrl_df.query("Date == @max_date")["Last_Price"].squeeze()
            # vamos ajustar com a variacao do usdbrl
            last_price = last_price * (1 + var_usdbrl)
            #vamos colocar na base na data de hoje
            usdbrl_df = pd.concat([usdbrl_df, 
                        pd.DataFrame({"Date":[today],
                                      "Asset":['bmfxclco curncy'], "Last_Price":[last_price]})])
            
            usdbrl_df["Date"] = pd.to_datetime(usdbrl_df["Date"])
        
        return usdbrl_df
    

    def __update_hist_px_last_intraday(self, hist_prices):
        
        tickers = list(hist_prices["Asset"].unique())
        px_last = self.get_table("px_last", index=True, index_name="Key").copy()
        # Selecionando todos os tickers que estao na tabela px_last
        px_last = px_last.query("Key in @tickers").reset_index()
        if ("Last_Updated" in px_last.columns) and ("Last_Updated" in hist_prices.columns):
            px_last = px_last.drop(columns=["Last_Updated"])
        
        # Vamos alterar a ultima ocorrencia desses tickers na hist_prices pelos valores na px_last
        # vamos fazer de forma vetorizada]
        hist_prices_columns = list(hist_prices.columns)
        hist_prices = hist_prices.merge(px_last, left_on=["Asset", "Date"],
                                        right_on=["Key", "last_update_dt"], how="left")
        hist_prices["Last_Price"] = np.where(~hist_prices['px_last'].isna(),
                                             hist_prices['px_last'], 
                                             hist_prices['Last_Price'])
        hist_prices = hist_prices[hist_prices_columns]
        
        return hist_prices       
        
        
    
    def __hist_prices_intraday_extensor(self, hist_prices):
        """ Completa a tabela de precos historicos com o preco intraday mais recente.

        Args:
            hist_prices (pd.DataFrame): dataframe de precos historicos
        """

        # Verificar cada Asset unico existente na tabela
        assets = hist_prices["Asset"].unique()
        today = dt.date.today()
        updated_dfs = []
        
        # vamos fazer cada ativo por vez
        for asset in assets:
            # vamos pegar a tabela de precos do ativo
            asset_prices = hist_prices.query("Asset == @asset")
            # Vamos pegar a data mais recente
            last_date = asset_prices["Date"].max().date()
            if last_date == today:
                # pega preço mais recente
                last_price = self.get_price(asset) 
                # atualiza na asset_prices nessa data
                asset_prices.loc[asset_prices["Date"] == last_date, "Last_Price"] = last_price
                updated_dfs.append(asset_prices.copy())
                continue
            # vamos pegar o ultimo preco presente no df
            last_price = asset_prices.query("Date == @last_date")["Last_Price"].squeeze()
            # vamos pegar a variacao ate o momento mais recente
            query_asset = asset
            if asset == 'bmfxclco curncy':
                query_asset = 'usdbrl curncy'
            variation = 0
            if today > last_date:
                variation = self.get_pct_change(query_asset, recent_date=today, previous_date=last_date)
            # vamos ajustar o preco com a variacao
            last_price = last_price * (1 + variation)
            # vamos colocar na base na data de hoje
            updated_dfs.append(pd.concat([asset_prices, 
                        pd.DataFrame({"Date":[today],
                                      "Asset":[asset], "Last_Price":[last_price]})]))
            
        updated_df = pd.concat(updated_dfs)
        updated_df["Date"] = pd.to_datetime(updated_df["Date"])
        
        return updated_df

        
    def get_prices(self, tickers=None, recent_date=dt.date.today(), previous_date=dt.date.today()-dt.timedelta(days=30),
                         period=None, currency="local", usdbrl_ticker="bmfxclco curncy", force_continuous_date_range=True,
                         holiday_location="all", get_intraday_prices=False, force_month_end=False):
        """
            Filtra o historico de preços pelos tickers e pelo periodo informado.

        Args:
            recent_date (dt.date, optional): data de fim. Por padrao, data de hoje.
            previous_date (dt.date, optional): data de inicio. Por padrao, 30 dias antes de hoje.
            tickers (list|set, optional): Lista de tickers que devem ser incluidos, quando existirem.
            period(str): ytd, mtd ou 'xm' onde 'x' é o numero de meses.
            currency(str): codigo de 3 caracteres da moeda ou 'all' para considerar a moeda local de cada ativo.
            period(str): ytd|mtd|'xm' onde 'x' é o numero de meses. Usara como base o parametro 'recent_date'
            holiday_location(str): all|any|us|bz ... ver metodo 'is_holiday'

        Returns:
            pd.DataFrame: Tabela de precos filtrada e convertida para moeda desejada
        """
        if period is not None:
            previous_date = self.get_start_period_dt(recent_date, period, holiday_location=holiday_location, force_bday=True,
                                                     force_month_end=force_month_end)

        if recent_date < previous_date:
            logging.info("Possivel inversao dos parametros de inicio e fim do periodo.")
            temp = recent_date
            recent_date = previous_date
            previous_date = temp

        if not self.price_tables_loaded:
            try:
                self.__load_table_group(["hist_px_last", "hist_non_bbg_px_last", "hist_vc_px_last", "all_funds_quotas",
                                     "custom_funds_quotas", "custom_prices", "px_last"])
            except FileNotFoundError:
                # Vamos tentar sem o custom_funds_quotas, pois pode nao existir ainda.
                self.__load_table_group(["hist_px_last", "hist_non_bbg_px_last", "hist_vc_px_last",
                                         "all_funds_quotas", "custom_prices", "px_last"])
                
        if tickers is None:
            #prices = self.hist_prices_table.query("Date <= @recent_date and Date >= @previous_date")
            # Nesse caso, tickers sera uma lista com todos os ativos da tabela de precos
            tickers = self.hist_prices_table["Asset"].unique()
        
        if isinstance(tickers, str):
                tickers = [tickers]
        
        tickers = [t.lower() for t in tickers] # padronizando tickers para lowercase

        prices = self.hist_prices_table.copy()

        surrogate_previous_date = previous_date - dt.timedelta(days=30)
        surrogate_recent_date = recent_date + dt.timedelta(days=30)
        prices = prices.query("Date <= @surrogate_recent_date and Date >= @surrogate_previous_date\
                                   and Asset.isin(@tickers)")
        
        if force_continuous_date_range:
            # Vamos ajustar as datas logo aqui, caso flag esteja ativa
            prices = prices.set_index("Date").groupby("Asset")\
                            .resample("D").last().ffill()\
                            .reset_index(level=0, drop=True).reset_index()
            # Precisará ser substituido pela linha abaixo no futuro
            # Porém ha perda de eficiencia, avaliar outras opções.
            #prices = prices.set_index("Date").groupby("Asset", group_keys=False)\
            #                .apply(lambda g: g.resample("D").last().ffill().assign(Asset=g.name),
            #                       include_groups=False).reset_index()
            

        if get_intraday_prices:
            prices = self.__hist_prices_intraday_extensor(prices)
        
        if currency != "local":

            # TODO:  Resolver problema de consistencia com ticker e ticker_bbg 

            assets= self.get_table("assets").copy().query("Type != 'ações_bdr' and Asset != 'spx eagle'")

            ticker_map = assets.query("~Ticker_BBG.isna() and Ticker_BBG != Ticker")[["Ticker", "Ticker_BBG"]].set_index("Ticker").to_dict("index")
            assets["Ticker"] = assets["Ticker"].apply(lambda x: ticker_map[x]["Ticker_BBG"] if x in ticker_map.keys() else x)
            ticker_to_location = assets[["Ticker", "Location"]].drop_duplicates()
            prices = pd.merge(prices, ticker_to_location, left_on="Asset", right_on="Ticker", how='left')[["Date", "Asset", "Last_Price", "Location"]]
            
            currency_map = {"bz":"brl","br":"brl", "us":"usd", "cn":"cad", "eur":"eur"}
            prices["Location"] = prices["Location"].apply(lambda x: currency_map.get(x, 'not found'))

            prices_by_location = []
            iter_prices = prices.groupby("Location")
            
            for p in iter_prices:
                
                if p[0] == 'not found':
                    assets_not_found = list(p[1]["Asset"].unique())
                    logging.info(f"currency_map nao suporta Location dos ativos {assets_not_found}.")
                    continue
                price_currency = p[0]
                
                converted_prices = self.convert_currency(p[1][list(set(p[1].columns) - {"Location"})], 
                                                                price_currency=price_currency, dest_currency=currency,
                                                                usdbrl_ticker=usdbrl_ticker, force_continuous_date_range=force_continuous_date_range,
                                                                holiday_location=holiday_location, get_intraday_prices=get_intraday_prices,
                                                                force_month_end=force_month_end)
                
                if not converted_prices.empty:
                    prices_by_location.append(converted_prices)
                    
            # Tratando o caso de nao haver conversao para nenhum dos tickers
            if len(prices_by_location) > 0:
                prices = pd.concat(prices_by_location)[["Date", "Asset", "Last_Price"]].sort_values(by=["Asset", "Date"])
            else:
                prices = pd.DataFrame({}, columns=["Date", "Asset", "Last_Price"])
        
        # Finalmente, vamos seguir filtrando pelo periodo desejado.
        prices = prices.query("Date <= @recent_date and Date >= @previous_date and Asset.isin(@tickers)")
        
        #if adjust_bmfxlcoc and ('bmfxclco curncy' in tickers) and (recent_date == dt.date.today()):
        #    max_date = prices.query("Asset == 'bmfxclco curncy'")["Date"].max()
        #    if max_date < dt.date.today(): # vamos colocar mais um dia usando usdbrl curncy
        #        var_usdbrl1d = self.get_pct_change('usdbrl curncy', 
        #                                           recent_date=dt.date.today(),
        #                                           previous_date=max_date)
        #        # vamos pegar o last_price em max_date
        #        last_price = self.get_price('bmfxclco curncy', px_date=max_date)
        #        # vamos ajustar com a variacao do usdbrl
        #        last_price = last_price * (1 + var_usdbrl1d)
        #        #vamos colocar na base na data de hoje
        #        prices = pd.concat([prices, 
        #                    pd.DataFrame({"Date":[dt.date.today()],
        #                                  "Asset":['bmfxclco curncy'], "Last_Price":[last_price]})])

        return prices
    

    def convert_currency(self, prices, price_currency, dest_currency, usdbrl_ticker="bmfxclco curncy",
                         force_continuous_date_range=True, holiday_location="all",
                         get_intraday_prices=False, force_month_end=False):
        
        if price_currency == dest_currency: return prices

        convertion_rule = {"brl_usd" : {"currency_ticker":usdbrl_ticker,
                                        "operation":"divide"},
                           "usd_brl" : {"currency_ticker":usdbrl_ticker,
                                        "operation":"multiply"},
                           "eur_usd" : {"currency_ticker":"usdeur curncy",
                                        "operation":"divide"},
                           "usd_eur" : {"currency_ticker":"usdeur curncy",
                                        "operation":"multiply"},
                           "usd_cad" : {"currency_ticker":"cad curncy",
                                        "operation":"multiply"},
                           "cad_usd" : {"currency_ticker":"cad curncy",
                                        "operation":"divide"}, 
                                        }
        
        convertion_data = convertion_rule.get(price_currency+"_"+dest_currency, None)
        if convertion_data is None:
            logging.info(f"Conversao de moeda nao disponivel para {price_currency} -> {dest_currency}.")
            prices = pd.DataFrame({}, columns=prices.columns)
            return prices
        convertion_ticker = convertion_data["currency_ticker"]
        convertion_operation = convertion_data["operation"]
        
        previous_date = prices["Date"].min()
        recent_date = prices["Date"].max()

        currencies = self.get_prices(convertion_ticker, previous_date=previous_date, recent_date=recent_date,
                                     force_continuous_date_range=force_continuous_date_range, 
                                     holiday_location=holiday_location, get_intraday_prices=get_intraday_prices,
                                     force_month_end=force_month_end).copy()
        if convertion_operation == "divide":
            currencies["Last_Price"] = 1/currencies["Last_Price"]
        
        prices = pd.merge(prices, currencies[["Date", "Last_Price"]].rename(columns={"Last_Price":"Currency"}), on="Date")[list(prices.columns) + ["Currency"]]
        
        prices["Last_Price"] = prices["Last_Price"] * prices["Currency"]

        return prices[list(set(prices.columns) - {"Currency"}) ]
        
        
    def get_data(self, ticker, flds, data_date=None, logger_level="trace"):
        
        flds = flds.lower().replace(" ","_")

        if flds == "px_last":
            return self.get_price(ticker, px_date=data_date, logger_level=logger_level)
        
        if data_date is None:
            # Vamos buscar o dado mais recente
            data_value = None
            try:
                data_value = self.last_all_flds[ticker+"_"+flds]["Value"]
            except AttributeError:
                self.__load_table_group(["last_all_flds"])
                try:
                    data_value = self.last_all_flds[ticker+"_"+flds]["Value"]    
                except KeyError:
                    if logger_level == "trace":
                        logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                    elif logger_level == "info":
                        logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                    else: # logger_level == "erro":
                        logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                    return None
            except KeyError:
                if logger_level == "trace":
                    logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                elif logger_level == "info":
                    logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                else: # logger_level == "erro":
                    logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}'.")
                return None
            
            # Formatando o valor retornado
            data_type = self.get_table("field_map").query("Field == @flds")["Value_Type"].squeeze()

            if data_type == 'numerical':
                return float(data_value)
            if data_type == "date":
                return dt.datetime.fromtimestamp(float(data_value))
            if data_type != "text":
                logging.info(f"field '{flds}' nao foi cadastrado na tabela field_map.")
            return data_value
        
        # Buscamos por dado numa data especifica. 
        hist_all_flds = self.get_table("hist_all_flds")
        data_value   = None
        try:
            data_value = hist_all_flds.query("Date <= @data_date and Field == @flds and Ticker == @ticker")["Value"]
            if len(data_value) == 0:
                logging.info(f"Dado de {flds} nao disponivel para o ticker '{ticker}' na data '{data_date}'.")
                return None
            data_value = data_value.tail(1).squeeze()
        except KeyError:
            logging.info(f"Não foi possivel acessar a coluna Value da tabela hist_all_flds.")
        
        # Verificando o formato
        data_type = self.get_table("field_map").query("Field == @flds")["Value_Type"].squeeze()
        
        if data_type == 'numerical':
            return float(data_value)
        if data_type == "date":
            return dt.datetime.fromtimestamp(float(data_value))
        if data_type != "text":
            logging.info(f"field '{flds}' nao foi cadastrado na tabela field_map.")
        return data_value


    def get_bdr_size(self, ticker):
        if ticker == 'mcor34 bz equity': 
            return 4 #TODO remover quando atualizacao da table for reestabelecida
        sizes = self.get_table("bdr_sizes", index=True, index_name="Ticker")
        # dropar coluna Last_Updated caso exista
        if "Last_Updated" in sizes.columns:
            sizes = sizes.drop(columns=["Last_Updated"])
        
        return sizes.loc[ticker.lower()].tail(1).squeeze()    


    def get_cash_movements(self, fund_name, ref_date):

        cash_movements = self.get_table("cash_movements")
        #cash_movements["Settlement Date"] = cash_movements["Settlement Date"].dt.date
        #cash_movements["Date"] = pd.to_datetime(cash_movements["Date"]).dt.date #Conversao para Date só funcionou dessa maneira
        cash_movements = cash_movements.query("(Fund == @fund_name) and (Date > @ref_date)")[["Type", "Volume"]]
        #cash_movements = cash_movements.loc[ ((cash_movements["Fund"] == fund_name) & (cash_movements["Date"] > ref_date)) ] [["Type", "Volume"]]
        #cash_movements.to_excel("temmmp.xlsx")
        cash_movements = dict(cash_movements.groupby("Type")["Volume"].sum())

        return cash_movements
    

    def get_avg_price(self, fund_name, asset_key, date=None):

        if date is None:
            date = dt.date.today()

        positions = self.get_table("hist_positions").query("Fund == @fund_name and Asset_ID == @asset_key and Date <= @date")
        
        if len(positions) > 0:
            return positions.tail(1).squeeze()["Avg_price"]
        
        return 0


    def get_term_debt(self, fund_name):

        term_debt = self.get_table("last_positions")
        term_debt = term_debt.loc [((term_debt["Asset"].str.contains("term debt"))&(term_debt["Fund"]==fund_name))][["#", "Avg_price"]]
        total_debt = -(term_debt["#"] * term_debt["Avg_price"]).sum()

        return total_debt

    
    def is_holiday(self, date,  location):
        """
        Args:
            date (dt.date): 
            location (str): 
                    'any'-> se é feriado em qualquer um dos lugares cadastrados\n
                    'all' -> se é feriado em todas as localidades da tabela\n
                    'us', 'bz', (...) -> para local especifico, com codigo presente na tabela\n
        Returns:
            bool: se é ou nao feriado
        """
        holidays = self.get_table("holidays")

        if location != "any" and location != "all":
            holidays = holidays.loc[holidays["Location"] == location]
        if location == "all":
            n_locations = len(holidays["Location"].unique())
            holidays = (holidays["Date"]
                                .value_counts().reset_index()
                                .query("count == @n_locations")
                                )

        return date in set(holidays["Date"].dt.date)

    
    def get_bday_offset(self, date, offset=1, location="bz"):
        """ Retorna dia util com offset dias pra frente ou pra tras.\n
                location (str): 
                    'any'-> se é feriado em qualquer um dos lugares cadastrados\n
                    'all' -> se é feriado em todas as localidades da tabela\n
                    'us', 'bz', (...) -> para local especifico, com codigo presente na tabela\n
        """
        offset_direction = 0
        i = 1
        if offset != 0:
            offset_direction = offset/abs(offset)
            i = abs(offset)
        
        while i > 0 :
            # Pegamos proxima data
            date = date + dt.timedelta(days=offset_direction)
            # Verificamos se eh dia util. Se for, contabilizamos.
            if (date.weekday() < 5) and (not self.is_holiday(date, location) ):
                i -= 1
            elif offset == 0:
                offset_direction = -1
        
        return date
    

    def get_bdays_count(self, recent_date, previous_date, location="bz"):
        """
        Calcula quantos dias uteis existem entre recent_date e previous_date
        (Exclusivo, ou seja, recent_date e previous_date nao sao contados)
        """
        counter = 0
        iter_date = recent_date - dt.timedelta(days=1) # primeiro dia nao eh contado

        while iter_date > previous_date:
            
            if (iter_date.weekday() < 5) and (not self.is_holiday(iter_date, location) ):
                counter += 1
            iter_date -= dt.timedelta(days=1)

        return counter
    

    def get_month_end(self, ref_date):

        ref_date = dt.date(ref_date.year, ref_date.month, 20) + dt.timedelta(days=20)
        return dt.date(ref_date.year, ref_date.month, 1) - dt.timedelta(days=1)

        
    def get_start_period_dt(self, ref_date, period, force_bday=False, holiday_location="all",
                            force_month_end=False):
        """ A partir da data informada e do periodo, retorna a data de inicio do periodo.

        Args:
            ref_date (dt.date): A data de referencia
            period (str): O periodo em questao dado em meses, ou ytd ou mtd. Ex.: '12m', '6m', 'ytd', 'mtd', '24m'
            force_bday (bool): Determina se a data retorna devera ser dia util\n
            holiday_location (str): \n
                                    "bz","us" -> considerar feriados num local especifico\n
                                    "all" -> considerar feriados globais apenas\n
                                    "any" -> considerar feriado em qualquer localidade (dentre bz e us)
        """
        period = period.lower()
        start_date = None
        if period[-1] == "m": 
            
            n_months = int(period.split("m")[0])

            if force_month_end:
                start_date = ref_date - pd.DateOffset(months=n_months)
                start_date = start_date.date()
                start_date = self.get_month_end(start_date)
            else:

                is_leap_date = ((ref_date.month == 2) and (ref_date.day == 29))

                if is_leap_date:
                    ref_date = ref_date-dt.timedelta(days=1)


                year_offset = n_months//12 # obtendo o numero de anos inteiros no periodo informado
                month_offset = n_months%12 # obtendo o numero de anos parciais 

                start_date = dt.date(ref_date.year-year_offset, ref_date.month, ref_date.day)
                start_date = start_date - month_offset * dt.timedelta(days=30)

                if is_leap_date:
                    start_date = start_date + dt.timedelta(days=10) # forcando avanco ao mes seguinte
                    # Retornando ao ultimo dia do mes anterior
                    start_date = dt.date(start_date.year, start_date.month, 1)-dt.timedelta(days=1)
                

        elif period == "ytd":
            start_date = dt.date(ref_date.year-1, 12, 31)
        
        elif period == "mtd":
            start_date = dt.date(ref_date.year, ref_date.month , 1) - dt.timedelta(days=1)
            
        # A partir de uma data pegar o trimestre anterior
        elif period == 'qtr':
            # Deve retornar sempre a ultima data do final do trimestre anterior
            current_quarter = (ref_date.month - 1) // 3 + 1
            start_of_current_quarter = dt.date(ref_date.year, (current_quarter - 1) * 3 + 1, 1)
            start_date = start_of_current_quarter - dt.timedelta(days=1) # Last day of previous quarter
        
        if force_bday:
            start_date = self.get_bday_offset(start_date, offset=0, location=holiday_location)
        

        return start_date
    

    def __calculate_benchmark_spxt_cash(self, previous_date, recent_date, prop_spxt=0.8, prop_cash=0.2, 
                                                cash_ticker="jpmutcc lx equity", spx_ticker="spxt index", usdbrl_ticker="bmfxclco curncy"):

        df = self.get_benchmark_spx_cash(previous_date=previous_date-dt.timedelta(days=40), recent_date=recent_date,
                                         spx_ticker=spx_ticker, prop_spx=prop_spxt, prop_cash=prop_cash, cash_ticker=cash_ticker,
                                         usdbrl_ticker=usdbrl_ticker).reset_index()
        #"inx index"
        previous_value = df.query("Date <= @previous_date").tail(1)["Benchmark"].squeeze()
        recent_value = df.query("Date <= @recent_date").tail(1)["Benchmark"].squeeze()

        return (recent_value/previous_value) -1
    

    def get_benchmark_spx_cash(self, previous_date:dt.date, recent_date:dt.date, prop_spx=0.8, prop_cash=0.2, currency="usd",
                               usdbrl_ticker="bmfxclco curncy", cash_ticker="jpmutcc lx equity", spx_ticker="spxt index"):
        """ 
        Obtem a serie historica do benchmark luxor a partir do indice s&p e caixa nas proporcoes desejadas.
        Args:
            previous_date (datetime.date): Data inicial desejada
            recent_date (datetime.date): Data final desejada
            prop_spx (float, optional): Proporcao s&p. Defaults to 0.8.
            prop_cash (float, optional): Proporcao caixa. Defaults to 0.2.
            currency (str, optional): Moeda desejada ('usd','brl'). Defaults to "usd".
            usdbrl_ticker (str, optional): Ticker do usdbrl para conversao. Defaults to "bmfxclco curncy".
            cash_ticker (str, optional): Ticker do ativo usado como caixa. Defaults to "jpmutcc lx equity".
            spx_ticker (str, optional): Ticker do ativo usado como s&p. Defaults to "spxt index".
        Returns:
            pandas.DataFrame: DataFrame contendo coluna Benchmark e Datas como index.
        """
        complementary_previous_date=previous_date
        
        if previous_date < dt.date(2018,12,31) and cash_ticker == 'jpmutcc lx equity':
            #logging.info(f"Nao ha datas anteriores a {dt.date(2018,12,31)} para o JPMUTCC. Sera usada essa.")
            previous_date = dt.date(2018,12,31)

        if previous_date < dt.date(2020,3,2) and cash_ticker == 'sofrindx index':
            #logging.info(f"Nao ha datas anteriores a {dt.date(2018,12,31)} para o JPMUTCC. Sera usada essa.")
            previous_date = dt.date(2020,3,2)
        


        data = self.get_prices(tickers=[spx_ticker, cash_ticker], previous_date=previous_date, currency=currency,recent_date=recent_date, 
                               usdbrl_ticker=usdbrl_ticker)
        
        if recent_date == dt.date.today():
            d = dt.datetime(recent_date.year, recent_date.month, recent_date.day)
            # Precisamos ajustar o ultimo preco para o mais recente
            last_prices = pd.DataFrame({"Date" : [d, d], 
                                        "Asset" : ["spxt index",cash_ticker], 
                                      "Last_Price" : [self.get_price("spxt index"), self.get_price(cash_ticker)]
                                    })
            data = pd.concat([data.query("Date < @d").copy(), last_prices])

        if complementary_previous_date != previous_date:
            # Entrar aqui significa que o periodo precisou ser ajustado, pois eh anterior a existencia do indice usado para o caixa
            # Nesse caso, vamos pegar todo o periodo que faltou e considerar retorno diario do FED FUND
            
            # Primeiro, obtemos o periodo completo do s&p
            data_spx = self.get_prices(tickers=[spx_ticker], previous_date=complementary_previous_date,
                                                 recent_date=recent_date, currency=currency, usdbrl_ticker=usdbrl_ticker)
            # Em seguida, vamos pegar o parcial do jpmutcc e completar com o treasury, 
            # Para isso, sera necessario criar uma serie normalizada a partir dos retornos diarios
            data_treasury = data.query("Asset == @cash_ticker").copy().set_index(["Date","Asset"]).pct_change().reset_index().dropna()
            cash_initial_date = min(data_treasury["Date"])
            complementary_treasury = self.get_prices(tickers=["fedl01 index"], previous_date=complementary_previous_date,
                                                 recent_date=recent_date, currency=currency, usdbrl_ticker=usdbrl_ticker)
            complementary_treasury["Last_Price"] = (1 + complementary_treasury["Last_Price"]/100) ** (1/360)-1
            complementary_treasury = complementary_treasury.query("Date < @cash_initial_date").copy()
            data_treasury = pd.concat([complementary_treasury, data_treasury])
            data_treasury["Asset"] = cash_ticker
            data_treasury["Last_Price"] = (data_treasury["Last_Price"] + 1).cumprod()
            data = pd.concat([data_spx, data_treasury])
            
                                                        

        # Gerando tabela de granularidade mensal, com as cotas mensais do indicador
        df = data.pivot(columns="Asset", index="Date",values="Last_Price").ffill().bfill().reset_index()
        df = df.groupby(df['Date'].dt.to_period('M')).last().reset_index(drop=True).set_index("Date")
        df = df.pct_change().fillna(0).reset_index()
        df["Benchmark"] = (df[spx_ticker] * prop_spx + df[cash_ticker] * prop_cash) + 1
        # Salvando a base mensal num novo df
        df_benchmark = df[["Date", "Benchmark"]].set_index("Date").cumprod()

        # Gerando base de granularidade diaria com o fator de retorno mtd com 80% spxt e 20% jpmutcc
        df = data.set_index("Date")
        df["Last_Price"] = df.groupby(["Asset"]).pct_change().fillna(0)+1
        df = df.rename(columns={"Last_Price":"Pct_Change"})

        df = df.pivot(columns="Asset", values="Pct_Change")
        
        df[cash_ticker] = df[cash_ticker].fillna(1) #df[cash_ticker].ffill() # como tende a ser constante, podemos estimar os valores na
        df[spx_ticker] = df[spx_ticker].fillna(1) # para o s&p por ser variavel, preencheremos com 0 sempre

        df["Year"] = df.index.year
        df["Month"] = df.index.month
        # Acumulando para encontrar o retorno MTD
        df_mtd_w = df.groupby(["Year", "Month"]).cumprod()
        # Ponderando para encontrar o benchmark MTD 80/20
        df_mtd_w["MTD"] = df_mtd_w[cash_ticker] * prop_cash + df_mtd_w[spx_ticker] * prop_spx

        # Agora que temos o fator MTD granularidade diaria e a cota mensal
        # Vamos colocar a cota mensal numa coluna da tabela de granulariade diaria
        # Primeiro, precisamos de uma juncao que compreenda ano e mes
        df_mtd_w["Year"] = df_mtd_w.index.year
        df_mtd_w["Month"] = df_mtd_w.index.month
        df_benchmark["Year"] = df_benchmark.index.year
        df_benchmark["Month"] = df_benchmark.index.month
        df_benchmark = df_benchmark.rename(columns={"Benchmark":"Previous_Month_Acc"})

        # shiftando para que seja sempre a rentabilidade acumulada ate o mes anterior.
        # Essa operacao tambem ira descartar qualquer acumulo feito numa data que nao for fim de mes.
        df_benchmark["Previous_Month_Acc"] = df_benchmark["Previous_Month_Acc"].shift(1).ffill().bfill()

        # Preenchemos entao uma coluna com a rentabilidade de cada mes anterior
        df = df_mtd_w.reset_index().merge(df_benchmark, on=["Month", "Year"], how="left")

        # Finalmente, o benchmark sera obtido atraves do acumulado anterior acumulado com o MTD atual
        df["Benchmark"] = df["Previous_Month_Acc"] * df["MTD"]

        return df[["Date", "Benchmark"]].set_index("Date")
        
    def get_quota_adjusted_by_amortization(self, fund_name, quota, date):
        """ Obtem cota ajudata pela amortização. Sendo usando para ajustar as cotas do Maratona
        """
        amortizations = {   # Amortizacao Bruta / PL antes da amortizacao
                "maratona" : [{"event_date" : dt.date(2024,1,4), "amortization_ratio" : 2_517_404.21/24_165_260.40},
                              {"event_date" : dt.date(2025,1,8), "amortization_ratio" : 950_000/27_633_373.46},
                              ],
            }
        # Verificando se ha amortizacoes para o ativo e aplicando.
        if fund_name in amortizations.keys():
            amortization = amortizations[fund_name]
            for amortization in amortization:
                if date < amortization["event_date"]:
                    quota =  quota * (1-amortization["amortization_ratio"])
        return quota


    def get_pct_change(self, ticker, recent_date= dt.date.today() , previous_date=dt.date.today()-dt.timedelta(days=1),
                        period=None, holiday_location="all", adjust_amortization=True, force_month_end=False):
        
        if period is not None:
            previous_date = self.get_start_period_dt(previous_date, period=period, holiday_location=holiday_location,
                                                     force_month_end=force_month_end)

        if recent_date < previous_date:
            logging.info("Possivel inversao dos parametros de inicio e fim do periodo.")
            temp = recent_date
            recent_date = previous_date
            previous_date = temp
        
        if ticker == 'benchmark luxor spx cash' and recent_date == dt.date.today():
            return self.__calculate_benchmark_spxt_cash(previous_date, recent_date, cash_ticker="sofrindx index")
        elif ticker == 'benchmark luxor sp500 85/15 cash' and recent_date == dt.date.today():
            return self.__calculate_benchmark_spxt_cash(previous_date, recent_date, prop_spxt=0.85, prop_cash=0.15,
                                cash_ticker='sofrindx index')


        last_price = self.get_price(ticker, px_date=recent_date)
        
        if last_price == 0 or last_price is None:
            return 0
        
        previous_price = self.get_price(ticker, px_date=previous_date)
        
        try:
            if (previous_price == 0) or (previous_date is None) or (previous_price is None):
                return 0
        except ValueError:
            logging.info(f"ValueError:\nticker:{ticker} previous_price: {previous_price} previous_date:{previous_date}")

        if adjust_amortization:
            last_price = self.get_quota_adjusted_by_amortization(ticker, last_price, recent_date)
            previous_price = self.get_quota_adjusted_by_amortization(ticker, previous_price, previous_date)

        return last_price/previous_price-1


    def get_pct_changes(self, tickers=None, recent_date=dt.date.today(),
            previous_date=dt.date.today()-dt.timedelta(days=1), period=None, currency="local",
            usdbrl_ticker="bmfxclco curncy", adjust_amortization=False, force_month_end=False):
        #TODO -> garantir que a tabela de precos esta sendo atualizada pelos precos no intraday
        if adjust_amortization:
            logging.info("Ajuste de amortizacao ainda NAO implementado para esse metodo.")
        # Aproveitando a get_prices, para realizar as filtragens
        pct_changes = self.get_prices(tickers=tickers, recent_date=recent_date,
                                      previous_date=previous_date, currency=currency,
                                      period=period, usdbrl_ticker=usdbrl_ticker,
                                       force_month_end=force_month_end, get_intraday_prices=True
                                       ).set_index("Date")
        if pct_changes.empty:
            return pd.DataFrame(columns=["Asset", "Pct_Change"]).set_index("Asset")
        
        pct_changes["Pct_Change"] = pct_changes.groupby("Asset").pct_change().fillna(0)+1
        pct_changes = pct_changes[["Asset", "Pct_Change"]]
        pct_changes["Pct_Change"] = pct_changes.groupby("Asset").cumprod()-1
        pct_changes = pct_changes.groupby("Asset").last()

        return pct_changes


    def __calculate_pct_table(self):

        

        self.hist_pct_change = self.hist_prices_table.copy().set_index("Date")
        self.hist_pct_change = self.hist_pct_change.groupby("Asset").pct_change().fillna(0)+1



    def get_positions(self, fund_name, date=dt.date.today(), recent_date=dt.date.today(), previous_date=None, period=None,
                      get_inner_positions=False, force_month_end=False):
        """
            Fornece um dicionario com as posicoes do fundo na data informada.
        """
        hist_pos = self.get_table("hist_positions").query("Fund == @fund_name")

        if (previous_date is None) and (period is None):
            # manter funcionamento antes da implementacao da funcionalidade de cosultar multiplas datas
            # Separamos posicoes historicas apenas do fundo que nos interessa antes da data informada
            hist_pos = hist_pos.loc[hist_pos["Date"].dt.date <= date]
            
            visited = set()
            positions = {}
            rows = hist_pos.to_dict("records") # Obtendo lista de rows(dicts) para iterar
            
            rows.reverse() # vamos iterar do primeiro ao ultimo

            for row in rows:
                if row["Asset_ID"] not in visited:
                    visited.add(row["Asset_ID"])
                    if row["#"] > 0.000001 or row["#"] < -0.000001:
                        positions[row["Asset_ID"]] = row["#"]

            if not get_inner_positions:
                return positions
            
            # Vamos ver se tem fundos da luxor
            # Vamos remover esse e explodir em posicoes internas
            inner_funds = {"lipizzaner_lipizzaner" : "lipizzaner",
                        "fund a_fund a" : "fund a"}
            for inner_fund in inner_funds.keys():
                if inner_fund in positions.keys():
                    inner_positions = self.get_positions(inner_funds[inner_fund], date,
                                                         get_inner_positions=True)
                    positions.pop(inner_fund)
                    positions.update(inner_positions)

            return positions
        
        # Obtendo data de inicio e validando datas
        assert(recent_date is not None)
        if period is not None:
            previous_date = self.get_start_period_dt(recent_date, period=period, force_month_end=force_month_end)
        assert(recent_date > previous_date)

        previous_or_before = hist_pos.query("Date <= @previous_date").groupby("Ticker").last().reset_index()
        previous_or_before["Date"] = previous_date

        after_previous = hist_pos.query("Date > @previous_date and Date <= @recent_date")
        positions = pd.concat([previous_or_before, after_previous])
        positions["Date"] = pd.to_datetime(positions["Date"])

        return positions


    def get_bdr_adj_price(self, asset_id, date, usdbrl_ticker="bmfxclco curncy"):
        
        ticker = asset_id.split("_")[-1]
        price_key = self.get_price_key(asset_id)
        bdr_size = self.get_bdr_size(ticker)
        usdbrl = self.get_price(usdbrl_ticker, px_date=date)

        return self.get_price(price_key, px_date=date) * usdbrl/bdr_size


    def normalize_trades(self, trades, currency, asset_id_columns="Asset_ID", usdbrl_ticker="bmfxclco curncy"):
        """ Para um dado dataframe de trades, converte para moeda indicada.
            Trades devem conter as colunas Asset, Ticker e Delta_Shares.
            BDR: Usa o peso do BDR e a quantidade de BDR operada para chegar na quantidade do ativo original.
            Financeiro: Corrigido pelo cambio de fechamento.

        Args:
            trades (pd.DataFrame): dataframe de trades, mais especificamente o output
                            de get_positions_and_movements.
            currency (str): brl; usd; all -> todas as moedas, no caso usd e brl
        """
        assert(currency in ["usd", "brl"])
        previous_date=trades["Date"].min()
        recent_date=trades["Date"].max()

        assets = self.get_table("assets")

        # tratando inconsistencia da Location do spx hawker
        spx_hawker_brl_tickers = [
            "SPX SEG HAWKER JAN22", "SPX SEG HAWKER FEB22", "SPX HAWKER CL AMAR22",
            "SPX SEG HAWKER APR22", "SPX HAWKER CL ASET18", "SPX SEG HAWKER JUN23", "SPX SEG HAWKER SEP23"]
        spx_hawker_brl_tickers = list(map(str.lower, spx_hawker_brl_tickers)) # colocando tudo para minusculo
        assets["Location"] = np.where(assets["Ticker"].isin(spx_hawker_brl_tickers), "bz", assets["Location"])


        # Salvando os nomes das colunas antes de editar a tabela.
        trades_columns = list(trades.columns)        


        # Adicionando algumas colunas que vamos precisar para conseguir distinguir os ativos
        trades = pd.merge(trades, assets[["Key", "Asset", "Ticker", "Type", "Location", "Ticker_BBG"]], left_on="Asset_ID", right_on="Key")
        
        # Achando quantidade do trade no ativo original -> usando peso do bdr 
        bdr_sizes = self.get_table("bdr_sizes", index=True, index_name="Ticker").reset_index()
        trades = pd.merge(trades, bdr_sizes, on="Ticker", how="left").rename(columns={"adr_adr_per_sh":"BDR_Size"})
        # Achando quantidade do trade no ativo original -> usando peso do bdr 
        # -> Partindo da premissa que sempre atualizamos o historico quando ha alteracao do peso (inplit/split do bdr)
        trades["Delta_Shares"] = np.where(trades["Type"] == 'ações_bdr', trades["Delta_Shares"] / trades["BDR_Size"], trades["Delta_Shares"])
        # Ajustando quantidades dos trades de localiza proporcionalmente:
        #lcam_rent_ratio = 0.4388444  #0.44 rent3 para cada lcam3
        #lzrfy_rent_ratio = 1 # 1 rent para cada lzrfy
        #trades["Delta_Shares"] = np.where(trades["Ticker"] == 'lcam3 bz equity', trades["Delta_Shares"] * lcam_rent_ratio, trades["Delta_Shares"])
        # Ajuste da lzrfy eh desnecessario ja que eh 1:1
        #trades["Delta_Shares"] = np.where(trades["Ticker"] == 'lzrfy us equity', trades["Delta_Shares"] * lzrfy_rent_ratio, trades["Delta_Shares"])

        #brkA_brkB_ratio = 1500
        #trades["Delta_Shares"] = np.where(trades["Ticker"] == 'brk/a us equity', trades["Delta_Shares"] * brkA_brkB_ratio, trades["Delta_Shares"])

        # Adicionando coluna de usdbrl de fechamento em cada dia
        hist_usdbrl = self.get_prices(usdbrl_ticker, previous_date=previous_date, recent_date=recent_date).rename(columns={"Last_Price": "USDBRL"})
        
        trades = pd.merge(trades, hist_usdbrl[["Date", "USDBRL"]], on="Date")
        
        # Criando colunas com financeiro normalizado.
        if currency == 'usd':
            trades["Trade_Amount"] = np.where(trades["Location"] == 'bz', trades["Trade_Amount"]/trades["USDBRL"], trades["Trade_Amount"])
            
        elif currency == 'brl':
            trades["Trade_Amount"] = np.where(trades["Location"] == 'us', trades["Trade_Amount"]*trades["USDBRL"], trades["Trade_Amount"])
        
        return trades[trades_columns]
    

    def normalize_price_key(self, df):
        """
            Adiciona a coluna 'Price_ID' no df informado representando uma chave normalizada para o preco do ativo desejado.
        Args:
            df (pandas.DataFrame): DataFrame que obrigatoriamente precisa conter 'Asset' e 'Ticker' como colunas. 
        """
        
        df_columns = list(df.columns)
        
        assets = self.get_table("assets")[["Key", "Asset", "Ticker", "Ticker_BBG",]].rename(columns={"Key":"Asset_ID"})

        assets["Price_Key"] = assets["Asset_ID"].apply(lambda x: self.get_price_key(x))
        asset_price_key_map = {"etf s&p" : 'voo us equity', "spx hawker": "spx fund spc - hawker portfolio class a shares september 2018 series",
                               "berkshire" : "brk/b us equity", "localiza" : "rent3 bz equity", "suzano":"suzb3 bz equity", 'tci': 'the childrens investment fund class h apr 2025'}
        assets["Price_Key"] = assets.apply(lambda row: asset_price_key_map[row["Asset"]] if row["Asset"] in asset_price_key_map else row["Price_Key"], axis=1)

        df = df.rename(columns={"Price_Key": "Price_Old_key"})
        df = pd.merge(df, assets[["Asset_ID", "Price_Key"]], on="Asset_ID")

        # Casos padroes |-> tratados na tabela asset, usando o get_price_key. Casos especificos adicionar no asset_price_key_map.
        #df["Price_Key"] = np.where((df["Ticker_BBG"] is None) or (df["Ticker_BBG"].isnull()), df["Ticker"], df["Ticker_BBG"])
        
        if "Price_Key" not in df_columns: df_columns.append("Price_Key")

        return df[df_columns]


    def calculate_average_price(self, df, asset_id="Asset_ID"):
        # Dictionary to store cumulative cost and total shares for each ticker
        ticker_info = {}

        # Function to update ticker information
        def __update_ticker(ticker, delta_shares, trade_amount):
            if ticker not in ticker_info:
                ticker_info[ticker] = {'cumulative_cost': 0, 'total_shares': 0, 'avg_price': 0}

            if delta_shares > 0:  # Buy trade
                ticker_info[ticker]['cumulative_cost'] += -trade_amount  # Trade amount is negative for buys

            elif delta_shares < 0:  # Sell trade
                # Update cumulative cost using the last average price
                ticker_info[ticker]['cumulative_cost'] -= ticker_info[ticker]['avg_price']* abs(delta_shares)

            ticker_info[ticker]['total_shares'] += delta_shares

            # Calculate average price
            if abs(ticker_info[ticker]['total_shares']) > 0.001:
                ticker_info[ticker]["avg_price"] = ticker_info[ticker]['cumulative_cost'] / ticker_info[ticker]['total_shares']

            else:
                ticker_info[ticker]["avg_price"] = np.nan  # Avoid division by zero

            return ticker_info[ticker]["avg_price"]
        
        # Apply the function to each row and create a new column for the average price
        df['Average_Price'] = df.apply(lambda row: __update_ticker(row[asset_id], row['Delta_Shares'], row['Trade_Amount']), axis=1)

        return df



    def calculate_adjusted_avg_price(self, df, groupby_column="Ticker"):
        """Recebe um DataFrame contendo as colunas Date, Ticker, Delta_Shares e Trade_Amount.
            Trade_Amount sera resultado do preco_medio anterior (ja calculado na transacao) 
            multiplicado pela quantidade operada. ATENCAO pois na venda nao tem a informacao
            do valor pelo qual o ativo foi vendido.

        Args:
            df (pandas.DataFrame):

        Returns:
            pandas.DataFrame: Adiciona as colunas Cumulative_Shares, Open_Position_Cost e Average_Price
        """
        # Sort the DataFrame by Ticker and Date for sequential processing
        df_sorted = df.sort_values([groupby_column, "Date", "Trade_Side"]) # sort by trade_side (para processar sempre a compra primeiro)
        df_columns = list(df.columns)

        # Calculate cumulative shares and trade value for each ticker
        df_sorted['Cumulative_Shares'] = df_sorted.groupby(groupby_column)['Delta_Shares'].cumsum()
        
        df_sorted = self.calculate_average_price(df_sorted)
        df_sorted["Average_Price"] = df_sorted.groupby(["Date", "Ticker", "Trade_Side"])["Average_Price"].ffill()#fillna(method="ffill")

        df_sorted["Open_Position_Cost"] = -abs(df_sorted["Cumulative_Shares"] * df_sorted["Average_Price"])

        return df_sorted[df_columns+["Cumulative_Shares", "Open_Position_Cost", "Average_Price"]]


    def __get_positions_and_movements(self, fund_name, tickers=None,
            recent_date=dt.date.today(), previous_date=dt.date.today()-dt.timedelta(days=1),
            period=None, holiday_location="all", currency="usd", usdbrl_ticker="bmfxclco curncy"):
        """
        Args:
            fund_name (str): 
            tickers (str|list|set, optional): Defaults to None.
            recent_date (datetime.date, optional): Defaults to dt.date.today().
            previous_date (datetime.date, optional): _description_. Defaults to dt.date.today()-dt.timedelta(days=1).
            period (str, optional): mtd|ytd|3m|6m|...|nm. Defaults to None.
            holiday_location (str, optional): any|bz|us|all. Defaults to "all".

        Returns:
            pandas.DataFrame: 
        """

        assert(currency in ["usd", "brl"])

        if period is not None:
            previous_date = self.get_start_period_dt(recent_date, period, holiday_location=holiday_location, force_bday=True)

        # Garantindo que a data inicial sera sempre dia util, assim eh certo de que havera preco de acao nessa data
        previous_date = self.get_bday_offset(previous_date, offset=0, location="any")
        lipi_manga_incorp_date = self.lipi_manga_incorp_date
        assets = self.get_table("assets")


        # Filtrando somente os trades desejados
        # lembrando que lipi precisa abrir em fund_A e manga_master (quando antes da incorporacao)
        # ha ainda um ajuste no lipi, que na data da incorporacao compra as posicoes do Manga (nao podemos tirar essas boletas) 
        trades = (self.get_table("trades")[["Date", "Fund", "Asset", "Ticker", "#", "Price", "Total", "Op Type"]]
                .rename(columns={"#":"Delta_Shares", "Total" : "Trade_Amount", "Op Type":"Op_Type"})
                .query("(Date > @previous_date and Date <= @recent_date) and Op_Type.isin(['a vista', 'ndf', 'termo', 'apl/resg fundos', 'vc capital call', 'vc'])"))

        fund_filter = [fund_name]
        if fund_name == 'lipizzaner':
            fund_filter += ["fund a"]
            if previous_date < lipi_manga_incorp_date:
                fund_filter += ["mangalarga master"]
        trades = trades.query("Fund in @fund_filter")

        trades = trades.query("Fund != 'lipizzaner' or Date != @lipi_manga_incorp_date").rename(columns={"Price" : "Exec_Price"}).copy()
        trades["Asset_ID"] = trades["Asset"] + "_" + trades["Ticker"]


        # Obtendo posicoes na data de inicio, e criando boletas de inicializacao
        initial_positions = []

        for f in fund_filter:
            fund_initial_pos = pd.DataFrame(self.get_positions(f, date=previous_date).items(), columns=["Asset_ID", "Delta_Shares"])
            if len(fund_initial_pos) == 0: continue
            fund_initial_pos["Fund"] = f
            fund_initial_pos[["Asset", "Ticker"]] = tuple(fund_initial_pos["Asset_ID"].str.split("_"))
            
            initial_positions.append(fund_initial_pos)
            
        
        if len(initial_positions) > 0:
            initial_positions = pd.concat(initial_positions)

            # Adicionando coluna de tipo, pois sera necessario tratar quando type == ações_bdr
            initial_positions = pd.merge(initial_positions, assets[["Key", "Type"]], left_on="Asset_ID", right_on="Key")

            initial_positions["Price_Key"] = initial_positions["Asset_ID"].apply(lambda x: self.get_price_key(x))
            initial_prices = (self.get_prices(tickers=list(initial_positions["Price_Key"]), previous_date=previous_date,
                                              recent_date=previous_date, force_continuous_date_range=True)
                                        .rename(columns={"Asset": "Price_Key", "Last_Price":"Exec_Price"})[["Price_Key", "Exec_Price"]])
            
            initial_positions = pd.merge(initial_positions, initial_prices, on=["Price_Key"])
            
            # Corrigindo preço de entrada das BDRs
            initial_positions["Exec_Price"] = initial_positions.apply(lambda row: row["Exec_Price"] if row["Type"] != 'ações_bdr' else self.get_bdr_adj_price(row["Asset_ID"], date=previous_date), axis=1)

            initial_positions["Trade_Amount"] = initial_positions["Delta_Shares"] * initial_positions["Exec_Price"] * (-1)
            initial_positions["Date"] = previous_date
            
        else:
            initial_positions = pd.DataFrame() # tratando caso inicial, onde nao ha posicoes no inicio

        trades = pd.concat([initial_positions, trades])[["Date", "Asset_ID", "Delta_Shares", "Exec_Price", "Trade_Amount"]]
        
        trades["Date"] = pd.to_datetime(trades["Date"])

        # Adicionando coluna pra marcar se eh compra ou venda. Sera usado na agregacao logo mais.
        #trades["Trade_Side"] = np.where(trades["Delta_Shares"] < 0, "sell", "buy")

        # Ordenando boletas, por padrao vamos sempre comprar antes de vender.
        trades = self.normalize_trades(trades, currency=currency, usdbrl_ticker=usdbrl_ticker).sort_values(by=["Date"], kind="stable")
        # Apos normalizar os trades, eh necessario recalcular o preco da boleta
        
        # Agrupando boletas de forma a ter apenas uma boleta por dia por codigo de ativo
        #trades = trades.groupby(["Date", "Asset_ID"]).agg({"Delta_Shares":"sum", "Exec_Price":"last", "Trade_Amount":"sum"}).reset_index()
        # Precisamos calcular novamente o preco correto de execucao do trade
        #trades["Exec_Price"] = abs(trades["Trade_Amount"])/abs(trades["Delta_Shares"])
        
        # Calculando posicao ao final de cada trade, preco medio e custo da posicao
        trades["Open_Quantity"] = trades.groupby(["Asset_ID"])["Delta_Shares"].cumsum()
        trades["Open_Quantity"] = np.where(abs(trades["Open_Quantity"]) < 0.00001, 0, trades["Open_Quantity"])
        trades = self.calculate_average_price(trades)
        trades["Average_Price"] = trades.groupby(["Asset_ID"])["Average_Price"].ffill()#fillna(method="ffill")
        
        # Vamos agregar novamente, agora para tirar o 'Trade_Side', passando a ter uma linha apenas por data
        #trades = trades.groupby(["Date", "Asset_ID"]).agg({"Delta_Shares":"sum", "Exec_Price":"last", "Trade_Amount":"sum",
        #                                                    "Open_Quantity":"last", "Average_Price" : "last", "Trade_Side":"last"}).reset_index()
        # Preco de execucao, necessita ser recalculado
        #trades["Exec_Price"] = abs(trades["Trade_Amount"])/abs(trades["Delta_Shares"])

        trades["Open_Position_Cost"] = (trades["Open_Quantity"] * trades["Average_Price"])

        return trades
    

    def get_positions_and_movements(self, fund_name, tickers=None,
            recent_date=dt.date.today(), previous_date=dt.date.today()-dt.timedelta(days=1),
            period=None, holiday_location="all", currency="usd", usdbrl_ticker="bmfxclco curncy"):
        
        """
        Args:
            fund_name (str): 
            tickers (str|list|set, optional): Defaults to None.
            recent_date (datetime.date, optional): Defaults to dt.date.today().
            previous_date (datetime.date, optional): _description_. Defaults to dt.date.today()-dt.timedelta(days=1).
            period (str, optional): mtd|ytd|3m|6m|...|nm. Defaults to None.
            holiday_location (str, optional): any|bz|us|all. Defaults to "all".

        Returns:
            pandas.DataFrame: 
        """

        df = self.__run_return_analysis(fund_name, tickers=tickers,
                                    recent_date=recent_date, previous_date=previous_date,
                                    period=period, holiday_location=holiday_location,
                                    currency=currency, agregate_by_name=False, usdbrl_ticker=usdbrl_ticker
                                    )

        # Vamos obter os precos de fechamento em cada dia
        # Preenchendo primeiro todo o historico
        prices_previous_date = (df["Date"].min() - dt.timedelta(days=100)).date()
        price_keys = list(df["Price_Key"].unique())
        prices = self.get_prices(
                    tickers=price_keys, previous_date=prices_previous_date, currency=currency,
                    get_intraday_prices=True, usdbrl_ticker=usdbrl_ticker
                    ).rename(columns={"Asset":"Price_Key"})
        
        #df = df.merge(prices, on=["Date", "Price_Key"], how="left")
        df = df.merge(prices, on=["Date", "Price_Key"]) #, how="left")
        # Finalmente, vamos atualizar com o preco mais recente do ativo na data de hoje
        #df_prev = df.query("Date < @dt.date.today()").copy()
        #df_today = df.query("Date == @dt.date.today()").copy()
        #assets = self.get_table("assets").rename(columns={"Key":"Asset_ID"})
        #df_today = df_today.merge(assets[["Asset_ID", "Location"]], on="Asset_ID")
        #if len(df_today) > 0:
        #    df_today["Last_Price"] = df_today.apply(lambda row: self.get_price(
        #                                        row["Price_Key"], currency=currency,
        #                                        usdbrl_ticker="usdbrl curncy",
        #                                        asset_location=row["Location"]), axis=1
        #                                        )
        #    df = pd.concat([df_prev, df_today])
        #else:
        #    df = df_prev
        
        df["Current_Position_Value"] = df["Open_Quantity"] * df["Last_Price"]

        df = df[["Date", "Asset_ID", "Price_Key", "Open_Quantity",
                "Delta_Shares", "Shares_Bought", "Shares_Bought_Cost", "Shares_Sold",
                "Amount_Sold", "Last_Price", "Current_Position_Value"]]
        
        # preenchendo Last_Price nulos com o do dia anterior para os mesmos asset_id
        df["Last_Price"] = df.groupby("Asset_ID")["Last_Price"].ffill()
        
        return df

    
    def run_return_analysis(self, fund_name, tickers=None, recent_date=dt.date.today(), previous_date=dt.date.today()-dt.timedelta(days=1),
                            period=None, holiday_location="all", usdbrl_ticker="bmfxclco curncy"):

        currency = "usd"
        positions_and_movements_usd = self.__run_return_analysis(fund_name, tickers=tickers, recent_date=recent_date,
                                                                        previous_date=previous_date, period=period,
                                                                        holiday_location=holiday_location, currency=currency,
                                                                        usdbrl_ticker=usdbrl_ticker)
        currency = "brl"

        positions_and_movements_brl = self.__run_return_analysis(fund_name, tickers=tickers, recent_date=recent_date,
                                                                        previous_date=previous_date, period=period,
                                                                        holiday_location=holiday_location, currency=currency,
                                                                        usdbrl_ticker=usdbrl_ticker)
        if (positions_and_movements_usd is None) and (positions_and_movements_brl is None): return None

        return pd.concat([positions_and_movements_usd, positions_and_movements_brl])


    def __expand_hist_positions(self, hist_positions, recent_date, previous_date, holiday_location="all"):

        #for asset_id in positions_and_movements["Asset_ID"].unique():
        #    first_trade_date = positions_and_movements[positions_and_movements['Asset_ID'] == asset_id].index.min()
        #    date_range = pd.date_range(start=first_trade_date, end=recent_date, freq='D')
        #    ticker_transactions = positions_and_movements[positions_and_movements['Asset_ID'] == asset_id]

        #    temp_df = pd.DataFrame({'Date': date_range, 'Asset_ID': asset_id})
        #    temp_df = temp_df.merge(ticker_transactions, on=['Date', 'Asset_ID'], how='left')
        #    columns_to_ffill = ["Asset_ID", 'Open_Quantity',"Open_Position_Cost", "Average_Price"]
        #    temp_df[columns_to_ffill] = temp_df[columns_to_ffill].ffill()
        #    columns_to_fill_zeros = ["Delta_Shares","Trade_Amount", "Exec_Price", "Shares_Bought",
        #                            "Shares_Sold", "Shares_Bought_Cost", "Amount_Sold", "Cost_Of_Stocks_Sold", "Result_Of_Stocks_Sold"]
        #    
        #    temp_df[columns_to_fill_zeros] = temp_df[columns_to_fill_zeros].fillna(0)
        #    
        #    daily_positions = pd.concat([daily_positions, temp_df])
        pass


    def __run_return_analysis(self, fund_name, tickers=None, recent_date=dt.date.today(),
            previous_date=dt.date.today()-dt.timedelta(days=1), period=None, holiday_location="all",
            currency="usd", agregate_by_name=True, usdbrl_ticker="bmfxclco curncy"):

        assert(currency in ["usd", "brl"])

        positions_and_movements = self.__get_positions_and_movements(fund_name, tickers, recent_date, previous_date, period, holiday_location,
                                                                     currency=currency, usdbrl_ticker=usdbrl_ticker)
        
        # -> Shares_Bought : Delta_Shares > 0
        positions_and_movements["Shares_Bought"] = np.where(positions_and_movements["Delta_Shares"] > 0, positions_and_movements["Delta_Shares"], 0)
        # -> Shares_Sold : Delta_Shares < 0
        positions_and_movements["Shares_Sold"] = np.where(positions_and_movements["Delta_Shares"] < 0, positions_and_movements["Delta_Shares"], 0)
        # -> Shares_Bought_Cost: eh o trade amount
        positions_and_movements["Shares_Bought_Cost"] = np.where(positions_and_movements["Delta_Shares"] > 0, abs(positions_and_movements["Trade_Amount"]), 0)
        # -> Amount_Sold : Shares_Sold * Exec_Price
        positions_and_movements["Amount_Sold"] = np.where(positions_and_movements["Delta_Shares"] < 0, abs(positions_and_movements["Trade_Amount"]), 0)
        # -> Cost_Of_Stocks_Sold : Shares_Sold * avg_price # vai dar ruim na zeragem, posso propagar o avg_price ao inves do cumulative_cost? Feito.
        positions_and_movements["Cost_Of_Stocks_Sold"] =abs( positions_and_movements["Shares_Sold"] * positions_and_movements["Average_Price"])
        # -> Result_Of_Stocks_Sold: Total_Sold - Cost_Of_Stocks_Sold
        positions_and_movements["Result_Of_Stocks_Sold"] = abs(positions_and_movements["Amount_Sold"]) - positions_and_movements["Cost_Of_Stocks_Sold"]
        
        #positions_and_movements.to_excel(f"testando_{currency}.xlsx")
        # Transformar granularidade pra diario somente aqui...
        agg_rule = {
            'Open_Quantity':"last", "Average_Price":"last",
            "Delta_Shares":"sum","Trade_Amount":"sum", "Exec_Price":"last", "Open_Position_Cost":"last", "Shares_Bought":"sum",
            "Shares_Sold":"sum", "Shares_Bought_Cost":"sum", "Amount_Sold":"sum", "Cost_Of_Stocks_Sold":"sum", "Result_Of_Stocks_Sold":"sum"
        }
        positions_and_movements = positions_and_movements.groupby(["Date", "Asset_ID"]).agg(agg_rule).reset_index()


        # diminuindo a granularidade de 1 linha por trade pra 1 linha por dia
        positions_and_movements = positions_and_movements.set_index("Date")
        
        daily_positions = pd.DataFrame()

        for asset_id in positions_and_movements["Asset_ID"].unique():
            first_trade_date = positions_and_movements[positions_and_movements['Asset_ID'] == asset_id].index.min()
            date_range = pd.date_range(start=first_trade_date, end=recent_date, freq='D')
            ticker_transactions = positions_and_movements[positions_and_movements['Asset_ID'] == asset_id]

            temp_df = pd.DataFrame({'Date': date_range, 'Asset_ID': asset_id})
            temp_df = temp_df.merge(ticker_transactions, on=['Date', 'Asset_ID'], how='left')
            columns_to_ffill = ["Asset_ID", 'Open_Quantity',"Open_Position_Cost", "Average_Price"]
            
            temp_df[columns_to_ffill] = temp_df[columns_to_ffill].infer_objects(copy=False).ffill()
            columns_to_fill_zeros = ["Delta_Shares","Trade_Amount", "Exec_Price", "Shares_Bought",
                                    "Shares_Sold", "Shares_Bought_Cost", "Amount_Sold", "Cost_Of_Stocks_Sold", "Result_Of_Stocks_Sold"]
            
            temp_df[columns_to_fill_zeros] = temp_df[columns_to_fill_zeros].astype(float).fillna(0)
            
            daily_positions = pd.concat([daily_positions, temp_df])

        positions_and_movements = daily_positions.copy()

        # -> Criar coluna price_key
        assets = self.get_table("assets")
        assets["Price_Key"] = assets["Key"].apply(lambda x: self.get_price_key(x))

        # -> Fazer merge com Asset_ID, colocando colunas Name, Class e Price_Key
        positions_and_movements = positions_and_movements.merge(assets[["Key", "Name", "Class", "Price_Key"]], left_on="Asset_ID", right_on="Key")

        if not agregate_by_name:
            return positions_and_movements

        # -> pegar precos e colocar no diario
        previous_date = positions_and_movements["Date"].min().date()
        prices = self.get_prices(tickers = list(positions_and_movements["Price_Key"].unique()), previous_date=previous_date-dt.timedelta(days=100), currency=currency,
                                                    usdbrl_ticker=usdbrl_ticker).rename(columns={"Asset":"Price_Key"})
        
        positions_and_movements = positions_and_movements.merge(prices, on=["Date", "Price_Key"])
        
        # -> Criar coluna Market_Value
        positions_and_movements["Current_Position_Value"] = positions_and_movements["Open_Quantity"] * positions_and_movements["Last_Price"]

        # -> Open_Result_Amount: Current_Position_Value - avg_price * Open_Quantity Se nao fizer assim vai dar problema no dia da zeragem
        positions_and_movements["Open_Result_Amount"] = positions_and_movements["Current_Position_Value"] - positions_and_movements["Open_Position_Cost"]

        # -> valido salvar uma versao nessa etapa para conferir
        #positions_and_movements.to_excel("testing.xlsx")
        # -> Apos essa agregacao, nao se pode mais usar o preco medio <-
        # -> Agrupar por Name
        positions_and_movements = positions_and_movements[[
            'Date', 'Asset_ID', 'Trade_Amount', # 'Delta_Shares', 'Exec_Price'
            'Open_Quantity', 'Open_Position_Cost', 'Name', #'Average_Price', 'Key'
            'Class', 'Price_Key', 'Current_Position_Value', # 'Last_Price'
            'Shares_Bought', 'Shares_Sold', 'Shares_Bought_Cost',
            'Amount_Sold', 'Cost_Of_Stocks_Sold', 'Result_Of_Stocks_Sold',
            'Open_Result_Amount']]

        agg_rule = { 'Asset_ID' : "last", 'Trade_Amount' : "sum", 'Open_Quantity' : "sum", 'Open_Position_Cost' : "sum",
            'Class' : "last", 'Price_Key' : "last", 'Current_Position_Value' : 'sum',
            'Shares_Bought' : "sum", 'Shares_Sold' : "sum", 'Shares_Bought_Cost' : "sum",
            'Amount_Sold' : "sum", 'Cost_Of_Stocks_Sold' : "sum", 'Result_Of_Stocks_Sold' : "sum",
            'Open_Result_Amount' : "sum"}

        positions_and_movements = positions_and_movements.groupby(["Date", "Name"]).agg(agg_rule).reset_index()

        # -> Acc_Result_Of_Stocks_Sold : Acc_Result_Of_Stocks_Sold.cumsum()
        positions_and_movements["Acc_Result_Of_Stocks_Sold"] = positions_and_movements.groupby("Name")["Result_Of_Stocks_Sold"].cumsum()
        # -> Tota_Result_Amount: Acc_Result_Of_Stocks_Sold + Open_Result_Amount
        positions_and_movements["Total_Result_Amount"] = positions_and_movements["Acc_Result_Of_Stocks_Sold"]  + positions_and_movements["Open_Result_Amount"]
        # -> Acc_Cost_Of_Stocks_Sold : Cost_Of_Stocks_Sold.cumsum()
        positions_and_movements["Acc_Cost_Of_Stocks_Sold"] = positions_and_movements.groupby("Name")["Cost_Of_Stocks_Sold"].cumsum()
        # -> Acc_Buy_Cost: Total_Bough.cumsum()
        positions_and_movements["Acc_Shares_Bought_Cost"] = positions_and_movements.groupby("Name")["Shares_Bought_Cost"].cumsum()

        # -> %_Closed_Result: Acc_Result_Of_Stocks_Sold/Acc_Cost_Of_Stocks_Sold
        positions_and_movements["%_Closed_Result"] = positions_and_movements["Acc_Result_Of_Stocks_Sold"]/abs(positions_and_movements["Acc_Cost_Of_Stocks_Sold"])
        # -> %_Open_Result: Current_Position_Value/Open_Position_Cost
        positions_and_movements["%_Open_Result"] = (positions_and_movements["Current_Position_Value"]/positions_and_movements["Open_Position_Cost"])-1
        # -> %_Total_Result: Total_Result_Amount/Acc_Buy_Cost
        
        positions_and_movements["Avg_Cost"] = (positions_and_movements[[
                                                "Name","Open_Position_Cost"]].groupby("Name")
                                                ["Open_Position_Cost"].cumsum())
        positions_and_movements["Avg_Cost"] = (positions_and_movements["Avg_Cost"])/(positions_and_movements
                                               .groupby("Name").cumcount() + 1)
        
        #positions_and_movements["%_Total_Result"] = positions_and_movements["Total_Result_Amount"]/positions_and_movements["Acc_Shares_Bought_Cost"]
        positions_and_movements["%_Total_Result"] = positions_and_movements["Total_Result_Amount"]/positions_and_movements["Avg_Cost"]
        # -> redefinir price_key e price -> Precisa tratar nessa funcao o caso a caso do ticker de preco que sera mostrado
        positions_and_movements = self.normalize_price_key(positions_and_movements)
        # A normalizacao pode acabar inserindo algum ticker generico que ainda nao estava calculado. Logo, temos que pegar os precos novamente.
        prices = self.get_prices(tickers = list(positions_and_movements["Price_Key"].unique()),
                                        previous_date=previous_date-dt.timedelta(days=100), currency=currency,
                                        usdbrl_ticker=usdbrl_ticker).rename(columns={"Asset":"Price_Key"})

        positions_and_movements = positions_and_movements.merge(prices[["Date", "Price_Key", "Last_Price"]], on=["Date","Price_Key"])
        
        positions_and_movements["Period"] = period
        positions_and_movements["Currency"] = currency
        # Consideramos como ativos atuais aqueles que possuem posicao aberta ou que foram encerradas no dia
        positions_and_movements["Is_Curr_Owned"] = abs(positions_and_movements["Open_Position_Cost"]) > 0.1
        positions_and_movements["Is_Curr_Owned_Prev"] = positions_and_movements.groupby("Name")["Is_Curr_Owned"].shift(1,fill_value=False)
        positions_and_movements["Is_Curr_Owned"] = positions_and_movements["Is_Curr_Owned"] | positions_and_movements["Is_Curr_Owned_Prev"]
        positions_and_movements = positions_and_movements.drop(columns=["Is_Curr_Owned_Prev"])

        positions_and_movements["Start_Date"] = positions_and_movements["Name"].map(positions_and_movements.groupby("Name")["Date"].min())
        positions_and_movements["End_Date"] = recent_date
        positions_and_movements["End_Date"] = pd.to_datetime(positions_and_movements["End_Date"])
        last_trades = positions_and_movements.query("Trade_Amount != 0").groupby("Name").tail(1).copy().set_index("Asset_ID")
        last_trades["End_Date"] = np.where(abs(last_trades["Open_Quantity"]) <0.00001, last_trades["Date"], last_trades["End_Date"])
        positions_and_movements["End_Date"] = positions_and_movements["Asset_ID"].map(last_trades["End_Date"])

        # Removendo erros de divisao por 0
        positions_and_movements["%_Closed_Result"] = np.where(abs(positions_and_movements["%_Closed_Result"]) == np.inf, 0, positions_and_movements["%_Closed_Result"])
        positions_and_movements["%_Open_Result"] = np.where(abs(positions_and_movements["%_Open_Result"]) == np.inf, 0, positions_and_movements["%_Open_Result"])
        positions_and_movements["%_Total_Result"] = np.where(abs(positions_and_movements["%_Total_Result"]) == np.inf, 0, positions_and_movements["%_Total_Result"])
        # Refinando, para garantir dados consistentes
        positions_and_movements["%_Open_Result"] = np.where(abs(positions_and_movements["Open_Quantity"]) < 0.00001, 0, positions_and_movements["%_Open_Result"])

        positions_and_movements["Security_Acc_Return"] = positions_and_movements[["Name","Last_Price"]].groupby(["Name"]).pct_change().fillna(0) + 1
        positions_and_movements["Security_Acc_Return"] = positions_and_movements[["Name","Security_Acc_Return"]].groupby(["Name"]).cumprod()-1

        
        positions_and_movements["Days_Since_Start"] = (positions_and_movements["Date"] - positions_and_movements["Start_Date"]).dt.days

        spx_prices = self.get_prices("inx index", recent_date=recent_date, previous_date=previous_date, currency=currency,
                                     usdbrl_ticker=usdbrl_ticker)[["Date", "Last_Price"]].rename(columns={"Last_Price" : "spx_index"})
        positions_and_movements = positions_and_movements.merge(spx_prices, on="Date", how="left")
        
        #positions_and_movements["spx_index"] = (positions_and_movements["spx_index"].pct_change().fillna(0)+1).cumprod()-1
    
        return positions_and_movements.rename(columns={"Price_Key":"Ticker"})


    def get_current_fx_data(self, fund, fx_ticker):
        """Calcula o PNL de FX de um fundo. -> CONSIDERANDO QUE EH USDBRL"""
        fx_positions = self.get_table("last_positions").query("Fund == @fund and Ticker == @fx_ticker").copy()
        fx_positions["Last_Price"] = fx_positions["Ticker"].apply(lambda x: self.get_price(x))
        fx_positions["Pnl_USD"] = fx_positions["#"] * ((fx_positions["Last_Price"]/fx_positions["Avg_price"]) - 1)
        fx_positions["Pnl_BRL"] = fx_positions["#"] * (fx_positions["Last_Price"] - fx_positions["Avg_price"])
        fx_positions["Exposure"] = fx_positions["#"] * fx_positions["Last_Price"]
        fx_positions = fx_positions[["Pnl_USD", "Pnl_BRL", "Exposure"]].squeeze().to_dict()

        return fx_positions
    

    def get_hist_cash_movements(self, fund, ref_date, bdays=10, 
            holiday_location="all", currency="usd", usdbrl_ticker = "bmfxclco curncy"):
        """Retorna o historico de caixa do fundo.
        Args:
            fund (str): nome do fundo
            currency (str): moeda (usd|brl)

        Returns:
            pandas.DataFrame: historico de caixa
        """

        ## TODO: Remover linhas com pnl e retorno vazios!


        fund = fund.replace(' ', '_').lower()
        previous_date = self.get_bday_offset(ref_date, -bdays,
                                        location=holiday_location)

        cash = self.get_table("hist_portfolios_concentration").query("Group.isin(['caixa','caixa_us']) and Fund_Name == @fund").copy() 
        cash["Date"] = cash["Date"].dt.date
        cash = cash.query("Date >= @previous_date").copy()
        # cash estara com ambos os caixas em R$ ou U$.
        # Para saber a moeda do caixa retornado, precisamos saber a moeda do fundo
        fund_key = fund.replace('_', ' ')
        fund = self.get_table("funds")
        fund['Country'] = fund['Country'].replace('br', 'bz')
        fund_location = fund.query("Short_Name == @fund_key")["Country"].squeeze()

        currency_location  = "us" if currency == "usd" else "bz"
        if fund_location != currency_location:
            usdbrl = self.get_prices(usdbrl_ticker, previous_date=cash["Date"].min(), recent_date=cash["Date"].max(),)
            usdbrl = self.usdbrl_clean_coupon_fix(usdbrl)
            usdbrl["Date"] = usdbrl["Date"].dt.date
            usdbrl = usdbrl.rename(columns={"Last_Price":"usdbrl"})
            cash = cash.merge(usdbrl[["Date", "usdbrl"]], on="Date", how="left")
            if fund_location == "bz":
                cash["Market_Value"] = cash["Market_Value"] / cash["usdbrl"]
            else:
                cash["Market_Value"] = cash["Market_Value"] * cash["usdbrl"]
            
            # Removendo coluna auxiliar
            cash = cash.drop(columns=["usdbrl"])

        # Vamos calcular o preco de fechamento com o rendimento do dia
        bz_cash_index = self.get_prices("bzacselc index", period="60m", currency=currency, usdbrl_ticker=usdbrl_ticker)
        bz_cash_index["Date"] = bz_cash_index["Date"].dt.date
        bz_cash_index = (bz_cash_index[["Date", "Last_Price"]]
                            .rename(columns={"Last_Price":"bz_cash_index"})
                            .set_index("Date").pct_change()
                            .fillna(0)+1).reset_index()
        
        us_cash_index = self.get_prices("sofrindx index", period="60m", currency=currency, usdbrl_ticker=usdbrl_ticker)
        us_cash_index["Date"] = us_cash_index["Date"].dt.date
        us_cash_index = (us_cash_index[["Date", "Last_Price"]]
                            .rename(columns={"Last_Price":"us_cash_index"})
                            .set_index("Date").pct_change()
                            .fillna(0)+1).reset_index()
        
        us_margin_cost = self.get_prices("sofr + 75bps", period="60m", currency=currency, usdbrl_ticker=usdbrl_ticker)
        try:
            us_margin_cost["Date"] = us_margin_cost["Date"].dt.date
        except AttributeError:
            logging.info(f'Erro ao converter usd_margin_cost para date. currency:{currency}, usdbrl_ticker:{usdbrl_ticker}\
                         {us_margin_cost.dtypes}')
            
        us_margin_cost = (us_margin_cost[["Date", "Last_Price"]]
                            .rename(columns={"Last_Price":"us_margin_cost"})
                            .set_index("Date").pct_change()
                            .fillna(0)+1).reset_index()
        
        cash = cash.merge(bz_cash_index, on="Date", how="left")
        cash = cash.merge(us_cash_index, on="Date", how="left")
        cash = cash.merge(us_margin_cost, on="Date", how="left")
        # Dependendo do ativo e da posicao a variacao no dia será diferente
        cash["Open_Price"] = 1
        cash["Close_Price"] = cash["bz_cash_index"]
        cash["Close_Price"] = np.where(cash["Group"] == "caixa_us",
                                       cash["us_cash_index"], cash["Close_Price"]
                                       )
        cash["Location"] = 'us'
        cash["Location"] = np.where(cash["Group"] == "caixa_us",
                                       'us', 'bz'
                                       )
        cash["Close_Price"] = np.where((cash["Market_Value"] < 0) & (cash["Group"] == "caixa_us") ,
                                        cash["us_margin_cost"], cash["Close_Price"]
                                        )

        cash = (cash[["Date", "Group", "Location", "Market_Value", "Open_Price", "Close_Price"]]
                    .rename(columns={"Date":"Today",
                                     "Market_Value":"Close_Mkt_Value"
                                     }))
        # Criando colunas necessarias para concatenar com o df do daily pnl
        cash["Close_Quantity"] = cash["Close_Mkt_Value"]

        cash["Type"] = cash["Group"]
        cash["Name"] = cash["Group"].str.replace("_", " ").str.title()
        cash["Asset_ID"] = cash["Type"].str.replace("_"," ")+"_"+cash["Type"].str.replace("_"," ")
        cash["Price_Key"] = cash["Type"]
        
        cash["Delta_Shares"] = cash.groupby(["Group"])["Close_Quantity"].diff().fillna(0)
        cash["Shares_Sold"] = np.where(cash["Delta_Shares"] < 0, cash["Delta_Shares"], 0)
        cash["Amount_Sold"] = cash["Shares_Sold"]
        cash["Shares_Bought"] = np.where(cash["Delta_Shares"] > 0, cash["Delta_Shares"], 0)
        cash["Shares_Bought_Cost"] = cash["Shares_Bought"]

        return cash


    def __fix_open_price(self, df_op_fix, currency, ref_date, previous_date,
                         usdbrl_ticker='bmfxclco curncy'):
        if len(df_op_fix) == 0:
            return pd.DataFrame()
        # Guardando a lista de colunas, para remover colunas auxiliares posteriormente
        columns_list= list(df_op_fix.columns)

        asset_ids = df_op_fix["Asset_ID"].unique()
        assets = self.get_table("assets").query("Key.isin(@asset_ids)")\
                    .copy()[["Key", "Ticker", "Currency Exposure"]].rename(columns={
                        "Key":"Asset_ID", "Currency Exposure" : "Currency_Exposure"
                    })

        df_op_fix = df_op_fix.merge(assets, on='Asset_ID')
        df_op_fix["Needs_Fix"] = df_op_fix["Currency_Exposure"] != currency
        
        df_fixed = df_op_fix.query("~Needs_Fix").copy()
        df_op_fix = df_op_fix.query("Needs_Fix").copy()


        local_prices = self.get_prices(df_op_fix["Ticker"].unique(), recent_date=ref_date,
                                        previous_date=previous_date, currency='local')
        local_prices["Open_Price"] = local_prices.groupby("Asset")["Last_Price"]\
                                        .shift(1).fillna(local_prices["Last_Price"])
        usdbrl = self.get_prices(usdbrl_ticker, recent_date=ref_date,
                                 previous_date=previous_date
                                 )[["Date", "Last_Price"]].rename(columns={"Last_Price":"usdbrl"})
        local_prices = local_prices.merge(usdbrl, on="Date").rename(
                                    columns={"Asset":"Ticker", "Date" : "Today"})
        
        # Considera apenas caso de brl e usd TODO: tratar outros casos que venham a existir
        if currency == 'usd':
            local_prices["Open_Price"] /= local_prices["usdbrl"]
        else:
            local_prices["Open_Price"] *= local_prices['usdbrl']
        
        # Substituindo Open_Price antigo pelo novo ja com a conversao correta de moeda
        df_op_fix = df_op_fix.drop(columns=["Open_Price"])
        df_op_fix = df_op_fix.merge(local_prices[["Today", "Ticker", "Open_Price"]], on=['Today', 'Ticker'])
        
        df_fixed = pd.concat([df_fixed, df_op_fix])
        # Removendo as colunas auxiliares
        df_fixed = df_fixed[columns_list]
        
        return df_fixed



    def calculate_daily_pnl(self, fund, ref_date, currency, holiday_location="all", bdays=10,
            group_filters=[], type_filters=[], classification_filters=[], inner_classification_filters=[], location_filters=[], asset_filters=[],
            currency_exposure_filters=[], include_cash=True, include_cash_debt=False, ticker_filters=[], annual_adm_fee=0,
            ignore_small_pnl=True, usdbrl_ticker="bmfxclco curncy"): #test_op_fix=False):
        """ Calcula o PnL do dia de cada ativo no fundo.
            (Nao inclui o PnL das taxas!).
        Args:
            fund (str): nome do fundo
            ref_date (str): data de referência do PnL
            currency (str): moeda (usd|brl)
            holiday_location (str, optional): refencia de feriados. Defaults to "all".
            bdays (int, optional): quantidade de dias uteis a serem considerados.
                                Defaults to 10.
        """
        # dia util anterior
        # Obtendo todas as posicoes e movimentacoes, dos ultimos dias
        previous_date = self.get_bday_offset(ref_date, -bdays,
                                        location=holiday_location)
        df = self.get_positions_and_movements(fund, previous_date=previous_date,
                                            recent_date=ref_date, currency=currency, usdbrl_ticker=usdbrl_ticker)
        assets = self.get_table("assets").rename(columns={"Key":"Asset_ID",
                                                          "Currency Exposure":"Currency_Exposure"})
        
        # Filtrando pelos ativos desejados
        if len(classification_filters) > 0:
            classification_filters = [x.lower() for x in classification_filters]
            assets = assets.query("Luxor_Classification.isin(@classification_filters)")
        elif len(inner_classification_filters) > 0:
            inner_classification_filters = [x.lower() for x in inner_classification_filters]
            assets = assets.query("Luxor_Inner_Classification.isin(@inner_classification_filters)")
        elif len(group_filters) > 0:
            group_filters = [x.lower() for x in group_filters]
            assets = assets.query("Group.isin(@group_filters)")
        elif len(type_filters) > 0:
            type_filters = [x.lower() for x in type_filters]
            assets = assets.query("Type.isin(@type_filters)")
        elif len(location_filters) > 0:
            location_filters = [x.lower() for x in location_filters]
            assets = assets.query("Location.isin(@location_filters)")
        elif len(asset_filters) > 0:
            asset_filters = [x.lower() for x in asset_filters]
            assets = assets.query("Asset.isin(@asset_filters)")
        elif len(ticker_filters) > 0:
            ticker_filters = [x.lower() for x in ticker_filters]
            assets = assets.query("Ticker.isin(@ticker_filters)")
        elif len(currency_exposure_filters) > 0:
            currency_exposure_filters = [x.lower() for x in currency_exposure_filters]
            assets = assets.query("Currency_Exposure.isin(@currency_exposure_filters)")
        # Fazemos uma juncao interna, mantendo somente as linhas filtradas acima
        df = df.merge(assets[["Asset_ID", "Name", "Group", "Type", "Location",
                               "Luxor_Classification"]], on="Asset_ID")

        df = df.sort_values(by="Date", ascending=True)
        df = df.rename(columns={
            "Date" : "Today",
            "Open_Quantity" : "Close_Quantity",
            "Last_Price" : "Close_Price",
            "Current_Position_Value" : "Close_Mkt_Value"
        })

        # Obtendo o preco de abertura
        df["Open_Price"] = df.groupby("Asset_ID")["Close_Price"].shift(1).fillna(df["Close_Price"])
        types_to_fix_open_price = ['ndf usdbrl']
        #if test_op_fix:
            
        df_op_fix = df.query("Type.isin(@types_to_fix_open_price)").copy()
        df_op_fix = self.__fix_open_price(df_op_fix, currency, ref_date, previous_date, usdbrl_ticker=usdbrl_ticker)
        
        df = df.query("~Type.isin(@types_to_fix_open_price)").copy()
        
        # Juntando dfs novamente
        df = pd.concat([df, df_op_fix])

        # Precisamos consertar o open_price do FX. (Deve ser convertido pelo spot de fechamento sempre)

        # Podemos puxar o caixa aqui e concatenar para as proximas operacoes
        if include_cash:
            cash = self.get_hist_cash_movements(fund, ref_date, currency=currency, bdays=bdays, holiday_location=holiday_location,
                                                usdbrl_ticker=usdbrl_ticker)
            cash["Today"] = pd.to_datetime(cash["Today"])
            cash = cash.query("Close_Mkt_Value >= 0").copy()
            cash["Luxor_Classification"] = 'fixed income'
            
            if len(location_filters) > 0:
                location_filters = [x.lower() for x in location_filters]
                cash = cash.query("Location.isin(@location_filters)").copy()
            
            df = pd.concat([df, cash])
            df = df.sort_values(by="Today", ascending=True)
        
        # Vamos segregar como dívida o caixa virado.
        if include_cash_debt:
            cash_debt = self.get_hist_cash_movements(fund, ref_date, currency=currency, bdays=bdays, holiday_location=holiday_location,
                                                     usdbrl_ticker=usdbrl_ticker)
            
            cash_debt["Today"] = pd.to_datetime(cash_debt["Today"])
            cash_debt = cash_debt.query("Close_Mkt_Value < 0").copy()
            cash_debt["Luxor_Classification"] = 'debt'
            # Invertendo os precos nesse caso para simular o juros corretamente.
            #cash_debt["Temp"] = cash_debt["Close_Price"]
            #cash_debt["Open_Price"] = cash_debt["Close_Price"]
            #cash_debt["Close_Price"] = cash_debt["Close_Mkt_Value"]
            #dropando temp
            #cash_debt = cash_debt.drop(columns="Temp")
            
            # Caixa virado no Brasil, vamos desconsiderar, pois na prática nao teremos.
            #cash_debt = cash_debt.query("Asset_ID != 'caixa_caixa' or Location != 'bz'").copy()
            #Optando por manter e retirar o PnL posteriormente, para nao perder a contribuicao dele pra aporte e resgate
            
            if len(location_filters) > 0:
                location_filters = [x.lower() for x in location_filters]
                cash_debt = cash_debt.query("Location.isin(@location_filters)").copy()
            
            df = pd.concat([df, cash_debt])
            df = df.sort_values(by="Today", ascending=True)

        # Vamos obter a data d-1
        df["Yesterday"] = (df.groupby("Asset_ID")["Today"].shift(1)
                            .fillna(df["Today"]-dt.timedelta(days=1))
                            )
        # Obtendo quantidade na abertura
        df["Open_Quantity"] = df.groupby("Asset_ID")["Close_Quantity"].shift(1).fillna(0)
        
        # Obtendo valor de mercado por ativo na abertura
        df["Open_Mkt_Value"] = df["Open_Quantity"] * df["Open_Price"]
        # Calculando precos de compas e vendas
        df["Buy_Price"] = np.where(df["Shares_Bought"] > 0, 
                            abs(df["Shares_Bought_Cost"]/df["Shares_Bought"]),0)
        df["Sell_Price"] = np.where(df["Shares_Sold"] < 0,
                            abs(df["Amount_Sold"]/df["Shares_Sold"]), 0)
        
        # Calculando PnL Diário (Caixa nao pode ser calculado aqui, pois o preco eh sempre 1)
        df["Pnl_Bought"] = abs(df["Shares_Bought"]) * (df["Close_Price"] - df["Buy_Price"])
        df["Pnl_Sold"] = abs(df["Shares_Sold"]) * (df["Sell_Price"] - df["Open_Price"])
        # Ajustando PnL sold. Quando for debt, a venda representa a divida sendo tomada
        # e a compra representa o pagamento da divida. Na primeira, ha juros e na segunda nao ha pnl.
        df['Pnl_Bought'] = np.where(df['Luxor_Classification'] == 'debt', 0, df['Pnl_Bought'])
        df['Pnl_Sold'] = np.where(df['Luxor_Classification'] == 'debt', 
                                  (df['Open_Price']-df['Close_Price'])*abs(df['Shares_Sold']), 0)
        
        df["Pnl_Unchanged"] = (df["Open_Quantity"] + df["Shares_Sold"]) * (df["Close_Price"] - df["Open_Price"])
        
        # O caixa no BZ pode estar virado temporariamente durante aportes/resgates de caixa_us, mas isso n estará gerando PnL
        df["Pnl_Unchanged"] = np.where((df["Asset_ID"] == 'caixa_caixa') & (df["Location"] == "bz") & (df["Location"] == "bz")& (df["Close_Mkt_Value"] < 0), 0, df["Pnl_Unchanged"])
        df["Pnl_Sold"] = np.where((df["Asset_ID"] == 'caixa_caixa') & (df["Location"] == "bz") & (df["Close_Mkt_Value"] < 0), 0, df["Pnl_Sold"])



        # Ajustar aqui as operacoes com logica de pnl e exposicao
        # Para nao considerar no AUM e no Cash Flow
        types_to_recalculate = ['ndf usdbrl']
        # Separando os dados em dois grupos, para editar um deles
        df_exposure = df.query("Type.isin(@types_to_recalculate)").copy()
        if len(df_exposure) > 0:
            df = df.query("~Type.isin(@types_to_recalculate)").copy()
            # Calculo especifico para pnl do FX.
            
            df_exposure["Pnl_Bought"] = df_exposure["Pnl_Bought"].astype('float')
            df_exposure["Pnl_Sold"] = df_exposure["Pnl_Sold"].astype('float')
            df_exposure["Pnl_Unchanged"] = df_exposure["Pnl_Unchanged"].astype('float')
            
            df_exposure["Total_Pnl"] = df_exposure["Pnl_Bought"] + df_exposure["Pnl_Sold"] \
                                        + df_exposure["Pnl_Unchanged"]
            
            df_exposure = df_exposure.set_index(["Asset_ID"])
            # Valor de mercado sera o PnL acumulado
            
            df_exposure["Total_Pnl"] = df_exposure.groupby(["Asset_ID"])["Total_Pnl"].cumsum()
            df_exposure = df_exposure.reset_index()
            df_exposure["Close_Mkt_Value"] = df_exposure["Total_Pnl"]
            df_exposure["Open_Mkt_Value"] = df_exposure["Close_Mkt_Value"].shift(1, fill_value=0)
            
            # Retirando qualquer possibilidade de impacto para aporte e resgate
            df_exposure["Shares_Bought_Cost"] = 0
            df_exposure["Amount_Sold"] = 0
            # TODO Pensar o que vai mudar no caso de uma zeragem parcial
            df_exposure = df_exposure.drop(columns="Total_Pnl")
            
            
            # Juntando dfs novamente
            df = pd.concat([df, df_exposure])

        # Calculando net de aporte e resgate por ativo
        df["Cash_Flow"] = abs(df["Shares_Bought_Cost"]) + -abs(df["Amount_Sold"])

        hist_dividends = self.get_dividends(fund, ref_date, previous_date, currency=currency,
                                            holiday_location=holiday_location, usdbrl_ticker=usdbrl_ticker)
        hist_dividends = pd.merge(assets[["Asset_ID", "Ticker"]],
                            hist_dividends, on="Ticker",how="left")[["Date", "Asset_ID", "Amount"]]
        hist_dividends = hist_dividends.rename(columns={"Date": "Today", "Amount":"Dividends"})

        df = df.merge(hist_dividends, on=["Today", "Asset_ID"], how="left")
        df["Dividends"] = df["Dividends"].fillna(0)
        
        
        df["Net_Subscriptions_Redemptions"] = df.groupby("Today")["Cash_Flow"].sum()

        df = df[["Today", "Name", "Asset_ID", "Group", "Type", "Location", "Luxor_Classification",
                "Open_Quantity", "Open_Mkt_Value", "Close_Quantity",
                "Shares_Bought", "Buy_Price", "Shares_Sold", "Sell_Price",
                "Dividends", "Close_Price", "Open_Price", "Close_Mkt_Value",
                "Cash_Flow", "Pnl_Bought", "Pnl_Sold", "Net_Subscriptions_Redemptions", "Pnl_Unchanged"]]
        

        # Calculando AUM no fechamento
        df = df.set_index("Today")
        df["Close_AUM"] = df.groupby("Today")["Close_Mkt_Value"].sum()
        df = df.reset_index()

        if annual_adm_fee != 0:
        # Incluir taxas de adm e gestao no calculo do PnL
        # Elas ja impactam o caixa, mas precisam ser consideradas no PnL
            daily_adm_fee = (1+abs(annual_adm_fee))**(1/365)-1
            df_fees = df[["Today", "Close_AUM"]].groupby("Today").last()
            df_fees["Pnl_Unchanged"] = -df_fees["Close_AUM"] * daily_adm_fee
            df_fees = df_fees.reset_index()
            df_fees["Asset_ID"] = "taxas e custos_tx adm"
            
            value_columns = df.columns[7:-2] # Sobrescreve com 0, menos para Pnl_Unchanged e Close_AUM
            
            df_fees[value_columns] = 0 # Para taxas, todos os outros valores nao importam.
            # Finalmente, falta colocar dados de name, type e group
            all_assets = self.get_table("assets").rename(columns={"Key":"Asset_ID"})
            
            df_fees = df_fees.merge(all_assets[["Asset_ID", "Name","Type", "Group", "Location"]], on="Asset_ID")
            if len(location_filters) > 0:
                location_filters = [x.lower() for x in location_filters]
                df_fees = df_fees.query("Location.isin(@location_filters)")

            df = pd.concat([df, df_fees])  
                        
        df["Daily_Pnl"] = df["Pnl_Unchanged"] + df["Pnl_Bought"] + df["Pnl_Sold"] + df["Dividends"]

        # Calculando PL Inicial Ajustado
        df = df.set_index("Today")
        df["Net_Subscriptions_Redemptions"] = df.reset_index().groupby("Today")["Cash_Flow"].sum()
        # Sera o valor de mercado da abertura somado com o net de aportes.
        # Racional: Resgates rentabilizam no dia (ja estao no inicial)
        #           Aportes rentabilizam no dia (nao estano no inicial)
        df["Open_AUM"] = df.reset_index().groupby("Today")["Open_Mkt_Value"].sum()
        df["Open_AUM_Adjusted"] = (df["Open_AUM"] +
                                    
                                    df["Net_Subscriptions_Redemptions"]*(df["Net_Subscriptions_Redemptions"] > 0)
                                    )
        
        df["Open_AUM_Adjusted"] = df["Open_AUM_Adjusted"].fillna(0)
        df["Daily_Attribution"] = np.where(df["Open_AUM_Adjusted"] == 0,0, df["Daily_Pnl"] / df["Open_AUM_Adjusted"])
        df["Daily_Return"] = df.reset_index().groupby("Today")["Daily_Attribution"].sum()

        # ao retornar, filtrar port Daily_Pnl != 0 e  not Daily_Pnl.isna()
        if ignore_small_pnl:
            return (df.reset_index()
                .sort_values(by="Today").query(''' (Daily_Pnl <= -0.01 or Daily_Pnl >= 0.01)\
                                            and not Daily_Pnl.isna()'''))
        return df.reset_index().sort_values(by="Today")

        #return df.reset_index().sort_values(by="Today")


    def get_dividends(self, fund_name, recent_date, previous_date=None, period=None, currency='usd', 
                      usdbrl_ticker='bmfxclco curncy', holiday_location='all'):

        if period is not None:
            previous_date = self.get_start_period_dt(recent_date, period=period, holiday_location=holiday_location)

        df = self.get_table("hist_dividends").query("Fund == @fund_name and Date >= @previous_date and Date <= @recent_date").copy()
        df = df.reset_index(drop=True)
        if currency == 'local':
            return df

        df_usd = df.query("Currency == 'usd'").copy()
        df_brl = df.query("Currency == 'brl'").copy()

        if currency == 'usd':
            df_brl_mod = self.convert_currency(df_brl[["Date", "Amount"]].rename(columns={"Amount":"Last_Price"}),
                                  price_currency="brl",
                                  dest_currency="usd"
                                  ).rename(columns={'Last_Price' : 'Amount'})
            df_brl.loc[df_brl_mod.index, 'Amount'] = df_brl_mod['Amount']
        
        if currency == 'brl':
            df_usd_mod = self.convert_currency(df_usd[["Date", "Amount"]].rename(columns={"Amount":"Last_Price"}),
                                  price_currency="usd",
                                  dest_currency="brl"
                                  ).rename(columns={'Last_Price':'Amount'})
            df_usd.loc[df_usd_mod.index, 'Amount'] = df_usd_mod['Amount']
        
        df = pd.concat([df_brl, df_usd])[['Date', 'Ticker', 'Amount']]

        if fund_name == 'lipizzaner':
            df_fund_a = self.get_dividends('fund a', recent_date, previous_date, period, currency, usdbrl_ticker, holiday_location)
            df = pd.concat([df, df_fund_a])

        return df
            


    def get_position_variation(self, fund_name, recent_date, previous_date):
        """
            Fornece um dataframe com a variacao das posicoes do fundo entre as datas. 
            Inclui tambem uma coluna de flag informando se a posicao foi zerada ou nao
            
        """
        
        # Pegamos as posicoes da data mais recente, transformando de dict para dataframe
        cur_positions = self.get_positions(fund_name, recent_date)
        cur_positions = pd.DataFrame(cur_positions.items(), columns = ["Key", "#_cur"])
        
        # Igual para as posicoes da data mais antiga
        prev_positions = self.get_positions(fund_name, previous_date)
        prev_positions = pd.DataFrame(prev_positions.items(), columns=["Key", "#_prev"])
        
        # Realizamos juncao externa na chave, mantendo assim dados nan (zeragens e ativos novos)
        diff = pd.merge(cur_positions, prev_positions, on="Key", how="outer").fillna(0)

        diff["Variation"] = diff["#_cur"] - diff["#_prev"]
        diff["Closed"] = diff["#_cur"] == 0

        return diff[["Key", "Variation", "Closed"]]

    
    def get_risk_metric(self, fund_name,  metrics=None, date=dt.date.today()):
        """
            Retorna as metricas de risco numa determinada data.
        
        Args:
            fund_name (str): nome do fundo correspontente
            metrics (str, list(str)): str da metrica desejada ou uma lista de strings
             para mais de uma metrica. Defaults to None (all available).
            date (datetime.date, optional): Data da metrica. Defaults to datetime.date.today().
        
        Returns:

            Pode retornar o valor de uma metrica especifica ou Dataframe quando 
            metrics passado for uma lista de metricas.
        
        """
        fund_name = fund_name.replace("_", " ")

        hist_metrics = self.get_table("hist_risk_metrics")
        hist_metrics = hist_metrics.loc[((hist_metrics["Fund"] == fund_name) & (hist_metrics["Date"].dt.date <= date) )].tail(1).reset_index(drop=True)

        if metrics is None:
            metrics = list(hist_metrics.columns)
            metrics.remove("Date")
            metrics.remove("Fund")
        
        try:
            if type(metrics) == list:

                return hist_metrics[metrics].astype(float)
        
            return float(hist_metrics[metrics].squeeze())
        except KeyError:
            logging.info(f"Metrica(s) {metrics} indisponivel(is)")
    

    def get_risk_metric_variation(self, fund_name, recent_date, previous_date, metrics=None):
        
        recent = self.get_risk_metric(fund_name, date=recent_date, metrics=metrics)
        previous = self.get_risk_metric(fund_name, date=previous_date, metrics=metrics)

        return recent - previous

    
    def get_group_results(self, previous_date= None, recent_date = None,  segments=None, currency="brl", inception_dates=None, period = None) -> pd.DataFrame:
        """Calcula e retorna o resultado de cada segmento.

        Args:
            recent_date (dt.date): Data inicial NAO inclusiva (sera filtrado por uma data anterior a essa.)
                                    Ex. Para considerar retorno ate o mes de marco, deve ser passada alguma data em abril.
            previous_date (dt.date): Data final
            segments (_type_, optional): Lista ou string com nome dos segmentos 
                desejados. Defaults to None. Quando None, retorna todos os segmentos existentes.

        Returns:
            pd.DataFrame: Retorno por segmento.
        """

        if (previous_date is not None) and (previous_date > recent_date):
            logging.info("Data inicial é menor que a data final. Parametros invertidos?")
            sys.exit()

        # Obtendo tabela de retornos historicos extraida do retorno consolidado
        group_results = self.get_table("luxor group results")[["Date", "Segment", "Return_Multiplier"]].copy()
        group_results["Date"] = pd.to_datetime(group_results["Date"])

        # Selecionando o periodo de tempo desejado
        if period is not None:
            recent_date = dt.date(recent_date.year,recent_date.month,20)+dt.timedelta(days = 15)
            previous_date = self.get_start_period_dt(recent_date, period=period)
            if period.lower() == "ytd":
                if recent_date.month == 1: # fechamento de dezembro! Vamos ter que ajustar o previous_date
                    previous_date = self.get_start_period_dt(recent_date-dt.timedelta(days=35), period=period)
                previous_date += dt.timedelta(days=1)

        group_results = group_results.query("Date >= @previous_date and Date < @recent_date").sort_values(by=("Date")).copy()

        if segments is not None:
            # Vamos deixar apenas os segmentos informados no parametro 'segments'
            if type(segments) is str:
                segments = [segments]
            if type(segments) is list:
                seg_filter = segments
            else:
                logging.info("'segments' precisa ser do tipo 'list' ou 'str'")
                sys.exit()
        
            group_results = group_results.query(" Segment.isin(@seg_filter)").copy()
        

        group_results = group_results.set_index("Date").groupby("Segment").prod() -1
        group_results = group_results.reset_index()

        # Retornos dos segmentos, por padrao, estarao em R$.
        # Para ver em US$ precisa ser feita a conversao.
        if currency == "usd":
            
            def __get_usdbrl_variation(segment):
                # ajustando janelas de inicio e fim, para pegar a variacao correta de usd no periodo ->  A base do grupo eh de retornos, a de usd eh de preços                
                usd_recent_date  = dt.date(recent_date.year, recent_date.month, 1) - dt.timedelta(days=1)
                usd_previous_date = dt.date(previous_date.year, previous_date.month, 1) -dt.timedelta(days=1)
                # Ainda, se a data for anterior ou igual ao inceptio date, vamos usar o incepion date
                #print(f"conversao usdbrl usando: previous_date:{usd_previous_date}  recent_date: {usd_recent_date}")
                if inception_dates is not None and segment in inception_dates.keys():
                    
                    sgmnt_inception = inception_dates[segment] -dt.timedelta(days=1) # subtraindo 1 dia para usar o fechamento do dia anterior ao inicio
                    usd_previous_date = sgmnt_inception if ((sgmnt_inception.year == previous_date.year) and (sgmnt_inception.month == previous_date.month)) else usd_previous_date
                                            #"bmfxclco curncy" -> converter usando usd cupom limpo
                
                delta_usdbrl = self.get_pct_change("bmfxclco curncy", previous_date=usd_previous_date, recent_date=usd_recent_date)
                #print(f"Segmento: {segment}  Retorno_BRL:{multiplier}  delta usdbrl={delta_usdbrl}   Retorno_USD: {(1+multiplier)/(1+delta_usdbrl)-1}")
                return delta_usdbrl

                                        
            # Convertendo para usd o que estiver em brl
            
            group_results["Return_Multiplier"] = group_results.apply(lambda row: (1 + row["Return_Multiplier"])/(1+__get_usdbrl_variation(row["Segment"])) -1, axis=1)

        group_results = group_results.set_index("Segment")

        return group_results

    def calculate_fund_particip(self, fund_name, fund_owned, date):
        """
            Informa o percentual que 'fund_name' possui do 'fund_owned'.

        Args:
            fund_name (str) 
            fund_owned (str)
            date (dt.date) 
        Returns:
            (float)
        """
        fund_name = fund_name.replace("_", " ")
        fund_owned_key = fund_owned + "_" + fund_owned

        # antes da data de incorporacao do manga master pelo lipi, 100% do manga master era do manga fic
        if fund_name == "mangalarga fic fia" and fund_owned == "mangalarga master":
            if date < dt.date(2022,12,9):
                return 1.0
            else: return 0
        # antes da data de incorporacao do manga master pelo lipi, 100% do fund_a era do manga master
        if fund_name == "mangalarga master" and fund_owned == "fund a":
            if date < dt.date(2022,12,9):
                return 1.0
            else: return 0
        # Adicionando mais um nivel de calculo 
        if fund_name == "mangalarga fic fia" and fund_owned == "fund a":
            if date < dt.date(2022,12,9):
                return self.calculate_fund_particip(fund_name, "mangalarga master", date) * self.calculate_fund_particip("mangalarga master", fund_owned, date)
            else:
                return self.calculate_fund_particip(fund_name, "lipizzaner", date) * self.calculate_fund_particip("lipizzaner", fund_owned, date)
        
        if fund_name == "mangalarga ii fic fia" and fund_owned == "fund a":
            if date < dt.date(2023,2,7):
                return self.calculate_fund_particip("mangalarga fic fia", "mangalarga master", date)
            else:
                return self.calculate_fund_particip(fund_name, "lipizzaner", date) * self.calculate_fund_particip("lipizzaner", fund_owned, date)

        position = self.get_table("hist_positions")

        # Busca otimizada pela posicao
        try:        
            position = (position["#"].to_numpy()[(
                            (position["Fund"].to_numpy() == fund_name)
                            &
                            (position["Asset_ID"].to_numpy() == fund_owned_key)
                            &
                            (position["Date"].dt.date.to_numpy() <= date)
                        )].item(-1))
        except (IndexError , KeyError):
            # nao havia participacao do fundo em questao na data informada
            return 0

        
        fund_owned_total_amount = self.get_table("all_funds_quotas")

        try:
            fund_owned_total_amount = (fund_owned_total_amount["#"].to_numpy()[(
                                            (fund_owned_total_amount["Fund"].to_numpy() == fund_owned)
                                            &
                                            (fund_owned_total_amount["Date"].dt.date.to_numpy() <= date)
                                            )].item(-1))
        except (IndexError , KeyError):

            # Algo deu errado
            return None

        return round(position/fund_owned_total_amount, 5) # Mantem 5 casas decimais de precisao

    def get_fund_aum(self, fund_name, date):

        hist_quotas = self.get_table("all_funds_quotas").query("Fund == @fund_name")

        return hist_quotas["#"].to_numpy()[hist_quotas["Date"].dt.date.to_numpy()==date].item(-1) * self.get_price(fund_name, px_date=date)
    

    def get_fund_numb_shares(self, fund_name, date):

        hist_quotas = self.get_table(fund_name+"_quotas")
        return hist_quotas["#"].to_numpy()[hist_quotas["Date"].dt.date.to_numpy()==date].item(-1)


    def get_delta_subscription_redemption(self, fund, previous_date, recent_date):
        
        hist_quotas = (self.get_table("all_funds_quotas")
                           .query("Fund == @fund and Date>= @previous_date and Date <= @recent_date")
                           .rename(columns={"#" : "Quota_Amnt"})[["Quota_Amnt", "Quota"]]
                           )
        hist_quotas["Delta_Quotas"] = hist_quotas["Quota_Amnt"].diff().fillna(0)
        # Nao eh necessario usar a cota do dia anterior. Caso precise, basta fazer o shift abaixo
        # hist_quotas["Quota"] = hist_quotas["Quota"].shift(1).fillna(0)
        delta = (hist_quotas["Delta_Quotas"] * hist_quotas["Quota"]).sum()
        return delta
    

    def is_month_end(self, date):
        cur_m = date.month
        return (date + dt.timedelta(days=1)).month != cur_m


    def get_fund_pnl(self, fund, previous_date, recent_date): #, orig_curncy=None, dest_curncy=None):
        
        # Nao ha nenhuma conversao de moeda a ser feita
        #if orig_curncy is None or dest_curncy is None or orig_curncy == dest_curncy:

        start_aum = self.get_fund_aum(fund, date = previous_date)
        end_aum = self.get_fund_aum(fund, date = recent_date)
        period_cash_flow = self.get_delta_subscription_redemption(fund, previous_date, recent_date)

        #if fund == "fund a":
        #    print()
        #    print(f"{fund}, prev:{previous_date} rec:{recent_date} pnl:{end_aum - start_aum - period_cash_flow} = {end_aum} - {start_aum} - {period_cash_flow}")

        return end_aum - start_aum - period_cash_flow
        
        # Desativando pois nao esta computando o resultado corretamente
        # Eh necessario converter de uma moeda para outra
        #location = self.get_table("funds").query("Fund == @fund")["Location"].squeeze()
        #end_date = recent_date
        #recent_date = previous_date
        #
        #total_pnl = 0
#
        #while recent_date < end_date:
#
        #    recent_date = self.get_next_attr_date(fund, previous_date, location, mode="week")
#
        #    if recent_date > end_date:
        #        recent_date = end_date
#
        #    # chamada recursiva, que roda apenas a primeira parte
        #    pnl = self.get_fund_pnl(fund, previous_date, recent_date)
        #    
        #    end_usdbrl = self.get_price("bmfxclco curncy", px_date=recent_date)
        #    
        #    if orig_curncy == "brl" and dest_curncy =="usd":
        #        total_pnl += pnl / end_usdbrl
        #    elif orig_curncy == "usd" and dest_curncy == "brl":
        #        total_pnl += pnl * end_usdbrl
        #    
        #    previous_date = recent_date
#
        #return total_pnl


    def get_eduardo_lipi_particip(self, date=dt.date.today()):
        
        funds_particip = (self.calculate_fund_particip("mangalarga fic fia", "lipizzaner", date=date) 
                        + self.calculate_fund_particip("mangalarga ii fic fia", "lipizzaner", date=date) 
                        + self.calculate_fund_particip("maratona", "lipizzaner", date=date)
                        + self.calculate_fund_particip("fund c", "lipizzaner", date=date)) 

        if funds_particip > 1:
            print(" ----> Atenção! Calculo de participacao ficou errado para o eduardo. <----")

        return 1 - funds_particip


    def get_next_attr_date(self, fund, start_date, location, mode): #funds_info):
        # Funcao auxiliar do attribution, permite pegar a proxima data valida para contabilizacao do attribution
        # Levar em consideracao que lipizzaner, antes de incorporar o manga, tinha também cota diaria.
        if mode == "day" or (fund == "lipizzaner" and start_date < dt.date(2022,12,9)):
            return self.get_bday_offset(date=start_date, offset=1, location=location)
        if mode == "week":
            thursday = 3 #weekday de quinta-feira (base da cota semanal)
            start_date_weekday = start_date.weekday()
            # Vamos setar a data como a proxima sexta e pegar o primeiro dia util anterior
            friday_offset = 8 if start_date_weekday == thursday else -(start_date_weekday - thursday - 1)
            next_date = self.get_bday_offset(date=start_date + dt.timedelta(days=friday_offset), offset=-1, location=location)

            # Caso com muitos feriados proximos. Vamos resolver pegando o proximo dia util, para facilitar.
            if next_date <= start_date:
                return self.get_bday_offset(date=start_date, offset=1, location=location)
            
            if next_date == dt.date(2023,1,12): next_date = dt.date(2023,1,16)

            if next_date.month != start_date.month:
                # houve troca de mes. Se o ultimo dia do mes nao for start_date, vamos retornos o final do mes
                month_ending = dt.date(start_date.year, start_date.month, 15) + dt.timedelta(days=25)
                month_ending = dt.date(month_ending.year, month_ending.month, 1) - dt.timedelta(days=1)
                # mas se start_date for o month_ending, entao esta correto retornar next_date.
                if month_ending == start_date:
                    return next_date 
                return month_ending
            return next_date
        logging.info("'mode' desconhecido.")


    def calculate_attribution(self, fund, previous_date, recent_date, fund_currency):
        """ Calcula o attribution do fundo informado para qualquer periodo.

        Args:
            fund (str): nome do fundo (lipizzaner, fund a, fund b, ...)
            previous_date (datetime.date): data inicial
            recent_date (datetime.date): data final
            fund_currency (str): 'brl' ou 'usd

        Returns:
            pandas.DataFrame: Dataframe contendo o attribution (% e pnl) por ativo no periodo.
        """

        # Acumulando os p&l's do periodo
        hist_attr = (self.get_table("hist_attr_base", index=True, index_name="Key")
                         .query("Fund == @fund and Start_Date>= @previous_date and End_Date <= @recent_date")
                         )
        # Corrigindo datas de inicio e fim, para datas validas considerando as janelas de attribution calculadas.
        previous_date = hist_attr["Start_Date"].min().date()
        recent_date = hist_attr["End_Date"].max().date()
        
        hist_attr = hist_attr[["p&l_brl","p&l_brl_curncy","p&l_usd","p&l_usd_curncy",  "attr_brl",  "attr_brl_curncy", "attr_usd", "attr_usd_curncy"]].groupby("Key").sum()

        #hist_attr = hist_attr[["p&l_brl","p&l_brl_curncy","p&l_usd","p&l_usd_curncy"]].groupby("Key").sum()


        # Vamos encontrar o total de p&l do periodo e a rentabilidade no periodo, em reais e em dolares
        end_usdbrl = self.get_price("bmfxclco curncy", recent_date)
        average_usdbrl = self.get_table("hist_px_last").query("Asset == 'usdbrl curncy' and Date >= @previous_date and Date <= @recent_date")["Last_Price"].mean()
        usdbrl_variation = self.get_pct_change("bmfxclco curncy", previous_date=previous_date, recent_date=recent_date)

        # Calculando pnl e rentab totais (ainda nao sabemos em qual moeda esta)
        total_pnl = self.get_fund_pnl(fund, previous_date, recent_date)
        total_rentab = self.get_pct_change(fund, previous_date=previous_date, recent_date=recent_date)
        others_pnl = total_pnl - hist_attr["p&l_"+fund_currency].sum()
        others_pnl_curncy = total_pnl - hist_attr["p&l_"+fund_currency+"_curncy"].sum()

        # Inicializando todas as possibilidades
        total_pnl_brl, total_pnl_usd, total_rentab_brl, total_rentab_usd = total_pnl, total_pnl, total_rentab, total_rentab
        others_pnl_brl, others_pnl_usd = others_pnl, others_pnl
        others_pnl_brl_curncy, others_pnl_usd_curncy = others_pnl_curncy, others_pnl_curncy
        
        # Encontrando moeda e corrigindo valores.
        if fund_currency == "usd":
            others_pnl_brl = others_pnl_brl * end_usdbrl
            others_pnl_brl_curncy = others_pnl_brl_curncy * end_usdbrl
            total_pnl_brl = hist_attr["p&l_brl"].sum() + others_pnl_brl
            total_rentab_brl = (1+total_rentab_usd)*(1+usdbrl_variation)-1
            # Nesse caso:
            # O pnl total precisa ter o mesmo sinal da rentabilidade total, senao algo esta errado.
            if total_pnl_brl * total_rentab_brl < 0:
                print(f"Rentabilidade e pnl com sinais trocados. Conferir '{fund}' de '{previous_date}' ate '{recent_date}'.")
                print(f"Obtendo pnl total a partir da rentabilidade e PL medio do periodo")
                fund_quotas = self.get_table("all_funds_quotas").query("Fund ==@fund and Date >= @previous_date and Date <= @recent_date")
                total_pnl_brl = (fund_quotas["#"] * fund_quotas["Quota"]).mean() * average_usdbrl * total_rentab_brl

        elif fund_currency == "brl":
            others_pnl_usd =others_pnl_usd / end_usdbrl 
            others_pnl_usd_curncy = others_pnl_usd_curncy / end_usdbrl
            total_pnl_usd = hist_attr["p&l_usd"].sum() + others_pnl_usd
            total_rentab_usd = ((1+total_rentab_brl) / (1+usdbrl_variation))-1
            # Nesse caso:
            # O pnl total precisa ter o mesmo sinal da rentabilidade total, senao algo esta errado.
            if total_pnl_usd * total_rentab_usd < 0:
                print(f"Rentabilidade e pnl com sinais trocados. Conferir '{fund}' de '{previous_date}' ate '{recent_date}'.")
                print(f"Obtendo pnl total a partir da rentabilidade e PL medio do periodo")
                fund_quotas = self.get_table("all_funds_quotas").query("Fund ==@fund and Date >= @previous_date and Date <= @recent_date")
                total_pnl_usd = (fund_quotas["#"] * fund_quotas["Quota"]).mean() / average_usdbrl * total_rentab_usd

        others_attr_brl = total_rentab_brl - hist_attr["attr_brl"].sum()
        others_attr_brl_curncy = total_rentab_brl - hist_attr["attr_brl_curncy"].sum()
        others_attr_usd = total_rentab_usd - hist_attr["attr_usd"].sum()
        others_attr_usd_curncy = total_rentab_usd - hist_attr["attr_usd_curncy"].sum()

        # Vamos inserir o row 'outros' com o que falta de pnl para atingir a rentabilidade do periodo
        hist_attr.loc["outros_outros"] = [others_pnl_brl, others_pnl_brl_curncy, others_pnl_usd, others_pnl_usd_curncy, others_attr_brl, others_attr_brl_curncy, others_attr_usd, others_attr_usd_curncy]
        
        #hist_attr.loc["outros_outros"] = [others_pnl_brl, others_pnl_brl_curncy, others_pnl_usd, others_pnl_usd_curncy]
        

        # Vamos calcular o % de atribuicao, proporcional a variacao da cota no periodo
        # Em reais
        #hist_attr["attr_brl"] = hist_attr.apply(lambda row: ((row["p&l_brl"])/abs(row["p&l_brl"])) * abs(row["p&l_brl"] * total_rentab_brl/total_pnl_brl), axis=1)
        #hist_attr["attr_brl_curncy"] = hist_attr.apply(lambda row: row["p&l_brl_curncy"] * total_rentab_brl/total_pnl_brl, axis=1)
        # Em dolares
        #hist_attr["attr_usd"] = hist_attr.apply(lambda row: row["p&l_usd"] * total_rentab_usd/total_pnl_usd, axis=1)
        #hist_attr["attr_usd_curncy"] = hist_attr.apply(lambda row: row["p&l_usd_curncy"] * total_rentab_usd/total_pnl_usd, axis=1)
        
        
        hist_attr["Start_Date"] = previous_date
        hist_attr["End_Date"] = recent_date
        
        return hist_attr        


    def calculate_drawdown(self, tickers, previous_date, recent_date, currency="local"):
        """Calcula o drawdown para um ativo ou um conjunto de ativos em cada data do perido fornecido.

        Args:
            tickers (str|list|set): ticker ou lista de tickers
            previous_date (dt.date): _description_
            recent_date (dt.date):

        Returns:
            pd.DataFrame: Seguinte DataFrame usando Date como index -> [[Asset, Period_Change, Previous_Peak, Drawdowns]]
        """

        df = self.get_prices(tickers=tickers, previous_date=previous_date, recent_date=recent_date, currency=currency).set_index("Date")

        df["Period_Change"] = df.groupby("Asset").pct_change().fillna(0) + 1
        df["Period_Change"] = df[["Asset", "Period_Change"]].groupby("Asset").cumprod()
        df["Previous_Peak"] = df[["Asset", "Period_Change"]].groupby("Asset").cummax()
        df["Drawdowns"] = (df["Period_Change"] - df["Previous_Peak"])/df["Previous_Peak"]
        
        return df


    def calculate_tracking_error(self, returns_ticker, benchmark_ticker, previous_date=dt.date.today()-dt.timedelta(days=365*2), recent_date=dt.date.today()-dt.timedelta(days=1), period=None, holiday_location="all"):
        """ Calcula o tracking error de uma serie de retorno com relacao ao benchmark.

        Args:
            returns_ticker (str): ticker da serie de retorno que sera testada
            benchmark_ticker (str): ticker da serie de retorno que sera usada para comparacao
            previous_date (dt.date): data de inicio do teste
            recent_date (dt.date): data de fim do teste
        Returns:
            _type_: _description_
        """
        
        if period is not None:
            previous_date = self.get_start_period_dt(recent_date, period=period, holiday_location=holiday_location)

        
        returns = self.get_prices([returns_ticker, benchmark_ticker], previous_date=previous_date, recent_date=recent_date, currency="usd")

        returns = returns.set_index("Date").pivot(columns="Asset").dropna(how="any")
        returns = returns.pct_change().dropna()
        
        returns.columns = [returns_ticker, benchmark_ticker]

        n_periods = len(returns)
        returns["Diff"] = (returns[returns_ticker] - returns[benchmark_ticker])**2
        
        tracking_error = 0
        if (n_periods - 1) > 0:
            tracking_error = (returns["Diff"].sum()/(n_periods - 1)) ** (1/2)
        

        return tracking_error


    def xirr(self, cashflows, dates):
        """
            Calcula o XIRR para uma serie de cash flows em datas especificas.

            :cashflows (numpy.array of float): cash flows (positive para entrada, negativo para saida)
            :dates (numpy.array of datetime64): datas correspondentes aos cash flows
            :return: XIRR
        """
        # Garantindo que dates eh um numpy array de datetime64
        if not isinstance(dates, np.ndarray) or dates.dtype.type is not np.datetime64:
            dates = np.array(pd.to_datetime(dates))

        t0 = dates[0]  # Reference date
        years = np.array([(date - t0).astype('timedelta64[D]').astype(int) / 365.25 for date in dates])
        
        def xnpv(rate):
            # Limiting the rate to avoid overflow and division by zero
            rate = max(min(rate, 1), -0.9999)
            return sum([cf / (1 + rate) ** yr for cf, yr in zip(cashflows, years)])
        
        def xnpv_prime(rate):
            rate = max(min(rate, 1), -0.9999)
            return sum([-yr * cf / (1 + rate) ** (yr + 1) for cf, yr in zip(cashflows, years)])
        
        try:
            # Using a conservative initial guess
            initial_guess = 0.1
            return newton(xnpv, x0=initial_guess, fprime=xnpv_prime)
        except (RuntimeError, OverflowError):
            # Return NaN if the calculation fails
            return np.nan
        
    
    def calculate_price_correlation(self, assets_data:dict, sample_frequency="monthly", period="12m", ref_date=dt.date.today()):
        """
        Calculate the correlation between assets in the columns of 'asset_prices'. The correlation is calculated using the formula:
        corr = (1 + r1*r2 + r1*r2*corr) / sqrt(1+r1**2) * sqrt(1+r2**2)
        where r1 and r2 are the returns of the assets and corr is the correlation between the returns.
        The correlation is calculated using the formula above and the returns are calculated using the formula:
        r = (price[t] - price[t-1]) / price[t-1]
        where t is the time period.
        The returns are calculated using the sample frequency and the lookback in months.
        assets_data: dict mapeando ticker para {Name:str, Key:str e Location:str(bz ou us)}
        sample_frequency: str, default "monthly". Frequencia de amostragem dos precos. Pode ser "daily", "weekly" ou "monthly"
        period: str, default '12m'. Periodo de calculo da correlacao. Deve ser 'ytd' ou o numero de meses seguido por 'm'
        """
        sample_frequency = sample_frequency.lower()
        period = period.lower()
        asset_prices = self.get_prices(tickers=set(assets_data.keys()) - {"usdbrl curncy"}, recent_date=ref_date,
                                        period=period, currency="usd", usdbrl_ticker="usdbrl curncy")
        usdbrl_prices = self.get_prices(tickers={"usdbrl curncy"}, period=period)
        asset_prices = pd.concat([asset_prices, usdbrl_prices])

        asset_prices = asset_prices.pivot(index="Date", columns="Asset", values="Last_Price").ffill()


        frequencies = {"daily":"B", "weekly":"W", "monthly":"ME"}
        asset_prices = asset_prices.resample(frequencies[sample_frequency]).last()
        #returns = asset_prices.pct_change(lookback_in_months)
        #returns = returns.dropna()
        correlations = asset_prices.corr()
        correlations.index.name = "Asset_Corr"
        correlations = correlations.reset_index()

        value_vars = correlations.columns
        correlations = correlations.melt(id_vars=["Asset_Corr"], value_vars=value_vars, value_name="Correlation", var_name="Asset").sort_values(by="Correlation").reset_index(drop=True)
        correlations["Key_Asset_Corr"] = correlations["Asset_Corr"].apply(lambda x: assets_data[x]["Key"])
        correlations["Key_Asset"] = correlations["Asset"].apply(lambda x: assets_data[x]["Key"])
        correlations.index.name="Order"
        correlations = correlations.reset_index()
        correlations["Comp_Key"] = correlations["Key_Asset_Corr"]+"_"+correlations["Key_Asset"]
        correlations["Frequency"] = sample_frequency.replace("ly","").title()
        period = period if int(period.replace("m","").replace("ytd","0")) < 12 else str(int(period.replace("m",""))/12).replace(".0","")+"y"
        correlations["Period"] = period.upper()
        
        return correlations
    

    def calculate_volatility(self, tickers, min_rolling_period_months, analysis_period_days, currency="local", sample_frequency="monthly", usdbrl_ticker="usdbrl curncy"):
        
        period = min_rolling_period_months + analysis_period_days//60 + 3
        prices = self.get_prices(tickers=tickers, period=str(period)+"m", currency=currency, usdbrl_ticker=usdbrl_ticker)

        year_size = 260

        if sample_frequency == "monthly":
            analysis_period_days = analysis_period_days//30 # numero de meses para rolling
            prices = prices.groupby("Asset").resample("ME", on="Date").last().reset_index(level=1).reset_index(drop=True).set_index("Date")
            year_size = 12
            
        elif sample_frequency == 'weekly':
            analysis_period_days = analysis_period_days//7 # numero de semanas para rolling
            prices = prices.groupby("Asset").resample("W", on="Date").last().reset_index(level=1).reset_index(drop=True).set_index("Date")
            year_size = 52

        elif sample_frequency == "daily":
            prices["Yesterday"] = prices["Date"] - dt.timedelta(days=1)
            prices["Equals_To_Yesterday"] = (prices["Last_Price"] == prices["Last_Price"].shift(1)) & (prices["Yesterday"] == prices["Date"].shift(1))
            prices = prices.query("~Equals_To_Yesterday")[["Date", "Asset", "Last_Price"]].copy().set_index("Date")
        
        
        prices["Previous_Price"] = prices.groupby("Asset")["Last_Price"].shift(1)
        prices["Return"] =np.log((prices["Last_Price"]/prices["Previous_Price"])).fillna(0)

        prices = prices[["Asset", "Return"]].groupby("Asset").rolling(window=analysis_period_days).std()*np.sqrt(year_size)*100

        prices = prices.reset_index().dropna().rename(columns={"Asset":"Ticker", "Return":"Volatility"})
        
        return prices


    def get_asset_name(self, ticker):

        assets = self.get_table("assets")
        name = assets.query("Ticker == @ticker")["Name"].squeeze()
        return name
                
                
    def simulate_portfolio_performance(self, portfolio: dict, portfolio_date: dt.date, adm_fee: float, performance_fee: float = 0):
            """
            Simula o desempenho de um portfólio com base em um dicionário de ativos e suas alocações iniciais.
            
            Parâmetros:
            - portfolio: dicionário com os ativos e suas alocações iniciais. Dicionário deve seguir o formato:\n
                {
                    "ticker1": peso1,
                    "ticker2": peso2,
                    ...
                    "tickerN": pesoN
                }, onde os pesos devem somar 1.
            - portfolio_date: data inicial do portfólio.
            - adm_fee: taxa de administração %.a.a
            - performance_fee: taxa de performance (opcional).
            
            Retorna:
            - DataFrame com o fator de correção da cota para cada dia a partir da data inicial do portfolio.
            """
            
            # Formatar os tickers para minusculas
            portfolio = {k.lower(): v for k, v in portfolio.items()}
            
            initial_portfolio = {
                "date" : portfolio_date,
                "assets" : portfolio,
            }
            
            # Criando dataframe com as colunas  Date|Ticker|Weight|
            positions = pd.DataFrame(initial_portfolio["assets"].items(), columns=["Ticker", "Weight"])
            positions["Date"] = initial_portfolio["date"]
            positions["Returns"] = 0
            positions["Daily_Attribution"] = 0.0
            positions["Daily_Portfolio_Return"] = 0.0
            
            tickers = positions["Ticker"].tolist()
            
            max_date = portfolio_date
            
            while max_date < dt.date.today():
                # Adicionando 1 dia
                new_date = max_date + dt.timedelta(days=1)
                daily_returns = self.get_pct_changes(tickers=tickers, previous_date=max_date, recent_date=new_date, currency="usd")
        
                daily_returns.index.name = "Ticker"

                new_day = positions.query("Date == @max_date").copy().set_index("Ticker")
                new_day["Returns"] = daily_returns
                new_day = new_day.reset_index()
                # Ajusta pesos considerando a atribuicao de retorno do dia anterior
                new_day["Weight"] = new_day["Weight"] + new_day["Daily_Attribution"]
                new_day["Date"]  = new_date
                
                new_day["Daily_Attribution"] = new_day["Weight"] * new_day["Returns"]
                new_day["Daily_Portfolio_Return"] = new_day["Daily_Attribution"].sum()

                positions = pd.concat([positions, new_day])
                max_date = new_date

            positions["Date"] = pd.to_datetime(positions["Date"])
            daily_returns = positions[["Date", "Daily_Portfolio_Return"]].groupby("Date").last()
            
            daily_returns["Acc_Returns"] = (1 + daily_returns["Daily_Portfolio_Return"]).cumprod()
            daily_returns["Acc_Returns_Adjusted_by_Taxes"] = np.where(daily_returns["Acc_Returns"] > 1,
                                                            ((daily_returns["Acc_Returns"] -1 ) * (1-performance_fee) + 1) - adm_fee/12,
                                                            daily_returns["Acc_Returns"] - adm_fee/12
                                                            )
            
            return daily_returns.reset_index()[["Date", "Acc_Returns_Adjusted_by_Taxes"]].rename(columns={"Acc_Returns_Adjusted_by_Taxes": "Factor"})
        
