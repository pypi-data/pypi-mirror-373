import datetime as dt
import io
import json
import time
import zipfile
from typing import Optional, Dict
import pandas as pd
import requests
from loguru import logger

from .auth import BTGApiError
from luxorasap.utils.dataframe import read_bytes

__all__ = [
    "request_portfolio",
    "check_report_ticket",
    "await_report_ticket_result",
    "process_zip_to_dfs",
    "request_investors_transactions_report",
    "request_fundflow_report"
]

_REPORT_ENDPOINT = "https://funds.btgpactual.com/reports/Portfolio"
_TICKET_ENDPOINT = "https://funds.btgpactual.com/reports/Ticket"
_INVESTOR_TX_ENDPOINT = (
    "https://funds.btgpactual.com/reports/RTA/InvestorTransactionsFileReport"
)
_FUNDFLOW_ENDPOINT = "https://funds.btgpactual.com/reports/RTA/FundFlow"
_REPORT_TYPES = {"excel": 10, "xml5": 81, "pdf": 2}


def request_portfolio(token: str, fund_name: str, start_date: dt.date, end_date: dt.date,
                      format: str = "excel") -> str:
    """Envia requisição de carteira; retorna *ticket*.
    
    Args:
        token: Token de autenticação.
        fund_name: Nome do fundo.
        start_date: Data de início.
        end_date: Data de fim.
        format: Formato do relatório ("excel", "xml5", "pdf").
    
    Returns:
        Ticket da requisição.
    """
    body = {
        "contract": {
            "startDate": f"{start_date}T00:00:00Z",
            "endDate": f"{end_date}T00:00:00Z",
            "typeReport": _REPORT_TYPES[format],
            "fundName": fund_name,
        },
        "pageSize": 100,
        "webhookEndpoint": "string",
    }
    r = requests.post(
        _REPORT_ENDPOINT,
        headers={"X-SecureConnect-Token": token, "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    if r.ok:
        return r.json()["ticket"]
    raise BTGApiError(f"Erro ao solicitar relatório: {r.status_code} – {r.text}")


def _download_url(download_url: str) -> bytes:
    r = requests.get(download_url, timeout=60)
    if r.ok:
        return r.content
    raise BTGApiError(f"Falha no download: {r.status_code} – {r.text}")


def check_report_ticket(token: str, ticket: str, *, page: Optional[int] = None) -> bytes:
    """Consulta único ticket; devolve bytes se pronto, lança BTGApiError caso contrário."""

    params = {"ticketId": ticket}
    if page is not None:
        params["pageNumber"] = str(page)

    r = requests.get(
        _TICKET_ENDPOINT,
        params=params,
        headers={"X-SecureConnect-Token": token},
        timeout=30,
    )
    # 1. Se resposta é ZIP direto → retornamos conteúdo
    try:
        payload = r.json()
    except json.JSONDecodeError:
        if r.ok:
            return r.content
        raise BTGApiError(f"Resposta inesperada: {r.status_code} – {r.text}")
    
    # 2. Caso contrário tenta decodificar JSON

    result = payload.get("result")
    
    if isinstance(result, str):
        if (result.lower() in "processando") or ('process' in result.lower()):
            raise BTGApiError("Processando")
    
    # 3. Quando pronto, result é JSON string com UrlDownload
    if isinstance(result, str):
        try:
            info: Dict[str, str] = json.loads(result)
            url = info["UrlDownload"]
            return _download_url(url)
        except Exception as exc:
            raise BTGApiError(f"Falha ao interpretar resultado: {exc}") from exc
    
    # 4. result pode ser uma lista de dados
    if isinstance(result, list):
        # Vamos tentar transformar num dataframe e retornar
        try:
            df = pd.DataFrame(result)
            return df
        except Exception as exc:
            raise BTGApiError(f"Falha ao converter resultado em DataFrame: {exc}") from exc

    raise BTGApiError(f"Formato de resposta desconhecido. Resultado:\n{result}")


def await_report_ticket_result(token: str, ticket: str, *, attempts: int = 10,
                               interval: int = 15) -> bytes:
    """Espera até que o relatório esteja pronto e devolve conteúdo binário.
    
    Args:
        token: Token de autenticação.
        ticket: Ticket da requisição.
        attempts: Número de tentativas.
        interval: Intervalo entre tentativas em segundos.
    
    Returns:
        Conteúdo binário do relatório (arquivo ZIP).
    
    Raises:
        BTGApiError: Se o relatório não ficar pronto ou falhar.
    """
    for i in range(attempts):
        try:
            return check_report_ticket(token, ticket)
        except BTGApiError as err:
            if "Processando" in str(err):
                logger.info(f"Ticket {ticket} pendente ({i+1}/{attempts})")
                time.sleep(interval)
                continue
            raise
    raise BTGApiError("Relatório não ficou pronto no tempo limite")


def process_zip_to_dfs(zip_bytes: bytes) -> dict[str, pd.DataFrame]:
    """Extrai todos os arquivos do ZIP e devolve DataFrames por nome."""
    out: dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            out[name] = read_bytes(zf.read(name), filename=name)
    
    return out


def request_investors_transactions_report( token: str, query_date: dt.date, *,
        distributors: list[str] | None = None, fund_names: list[str] | None = None,
        consolidate_by_account: bool = True, page_size: int = 100) -> str:
    """
    Gera um ticket para o relatório de transações de cotistas (RTA).
    Args:
        token: Token de autenticação.
        query_date: Data da consulta.
        distributors: Lista de nomes de distribuidores (opcional).
        fund_names: Lista de nomes de fundos (opcional).
        consolidate_by_account: Consolidar por conta (default True).
        page_size: Tamanho da página (default 100).
        
    Retorna *ticket* (string) a ser usado em `await_report_ticket_result`.
    """
    body = {
        "contract": {
            "distributors": distributors or [],
            "queryDate": f"{query_date.isoformat()}T00:00:00Z",
            "accountNumber": "",
            "consolidateByAccount": str(consolidate_by_account).lower(),
            "fundNames": fund_names or [],
        },
        "pageSize": page_size,
        "webhookEndpoint": "string",
    }

    r = requests.post(
        _INVESTOR_TX_ENDPOINT,
        headers={"X-SecureConnect-Token": token, "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    if r.ok:
        return r.json()["ticket"]
    raise BTGApiError(
        f"Erro InvestorTransactionsFileReport: {r.status_code} – {r.text}"
    )
    
    
def request_fundflow_report( token: str, start_date: dt.date,
        end_date: dt.date, *, fund_name: str = "", date_type: str = "LIQUIDACAO", page_size: int = 100) -> str:
    """Dispara geração do **Fund Flow** (RTA) e devolve *ticket*.

    Args:
        token: JWT obtido via :pyfunc:`luxorasap.btgapi.get_access_token`.
        start_date,end_date: Datas do intervalo desejado.
        fund_name: Nome do fundo conforme BTG. String vazia retorna as movimentacoes para todos os fundos.
        date_type: Enum da API (`LIQUIDACAO`, `MOVIMENTO`, etc.).
        page_size: Página retornada por chamada (default 100).

    Returns
    -------
    str
        ID do ticket a ser acompanhado em :pyfunc:`await_fundflow_ticket_result`.
    """

    body = {
        "contract": {
            "startDate": f"{start_date}T00:00:00Z",
            "endDate": f"{end_date}T00:00:00Z",
            "dateType": date_type,
            "fundName": fund_name,
        },
        "pageSize": page_size,
        "webhookEndpoint": "string",
    }

    r = requests.post(
        _FUNDFLOW_ENDPOINT,
        headers={"X-SecureConnect-Token": token, "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    if r.ok:
        return r.json()["ticket"]
    raise BTGApiError(f"Erro FundFlow: {r.status_code} - {r.text}")