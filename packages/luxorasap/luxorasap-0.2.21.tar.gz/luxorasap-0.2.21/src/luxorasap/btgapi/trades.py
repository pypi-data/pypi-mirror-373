import time
from typing import List, Dict

import pandas as pd
import requests
from loguru import logger

from .auth import BTGApiError

__all__ = [
    "submit_offshore_equity_trades",
    "get_submitted_transactions",
    "await_transaction_ticket_result",
]

_EP_SUBMIT_TEST = "https://funds-uat.btgpactual.com/offshore/TradeOffShore/Equity"
_EP_SUBMIT_PROD = "https://funds.btgpactual.com/offshore/TradeOffShore/Equity"
_EP_TICKET_TEST = "https://funds-uat.btgpactual.com/offshore/Ticket"
_EP_TICKET_PROD = "https://funds.btgpactual.com/offshore/Ticket"

_MARKET_IDS = {
    "equity": 20,
    "future": 22,
    "bonds": 24,
    "repo": 28,
    "portfolio_swap": 29,
    "interest_rate_swap": 30,
    "performance_swap": 31,
    "variance_swap": 32,
    "equity_option": 33,
    "future_option": 34,
    "fx_option_vanilla": 35,
    "fx_option_barrier": 36,
    "fx": 25,
}


def submit_offshore_equity_trades(token: str, trades: list[dict], *, test_env: bool = True) -> str:
    """
    Submete lista de trades de Equity Offshore para a API do BTG.

    Args:
        token: Token de autenticação.
        trades: Lista de dicionários representando os trades. Cada dict deve ter
            a estrutura esperada pela API. Modelo:
            [{
                "currency": "USD",
                "price": "60.12",
                "productCodeValue": "...",
                "glAccount": "...",
                "primeBroker": "...",
                "side": "Buy",
                "tradeQuantity": "1000",
                "commissionAmount": "12.50",
                "settlementCurrency": "USD",
                "fXRate": "1.0",
                "externalReference": "TRADE-001",
                "counterparty": "...",
                "fundNickname": "my_fund",
                "orderIdentification": "...",
                "book": "some_book",
                "tradeDate": "2025-02-19T16:03:53.596Z"
                }]

        test_env: Ambiente de teste (True) ou produção (False).

    Returns:
        Ticket da requisição.

    Raises:
        BTGApiError: Se a requisição falhar.
        
    """
    url = _EP_SUBMIT_TEST if test_env else _EP_SUBMIT_PROD
    r = requests.post(
        url,
        headers={
            "X-SecureConnect-Token": token,
            "Content-Type": "application/json-patch+json",
        },
        json={"results": trades},
        timeout=30,
    )
    if r.status_code in (200, 201):
        ticket = r.json()["ticket"]
        logger.info("Trades submetidos, ticket %s", ticket)
        return ticket
    raise BTGApiError(f"Falha no submit: {r.status_code} – {r.text}")


def get_submitted_transactions(token: str, *, ticket_id: str = "", start_date: str = "",
        end_date: str = "", market: str = "", test_env: bool = True) -> Dict:
    """Consulta status detalhado de ticket ou filtro de datas/mercado.
    Args:
        token: Token de autenticação.
        ticket_id: ID do ticket (opcional).
        start_date: Data de início (opcional, formato YYYY-MM-DD).
        end_date: Data de fim (opcional, formato YYYY-MM-DD).
        market: Mercado (opcional. Valores válidos: "equity", "future", "bonds", "repo",
            "portfolio_swap", "interest_rate_swap", "performance_swap", "variance_swap",
            "equity_option", "future_option", "fx_option_vanilla", "fx_option_barrier", "fx"]).
        test_env: Ambiente de teste (True) ou produção (False).

    Returns:
        Dicionário com os dados da resposta.

    Raises:
        BTGApiError: Se a requisição falhar ou a resposta for inválida.
        
    """

    base_url = _EP_TICKET_TEST if test_env else _EP_TICKET_PROD

    if ticket_id:
        params = {"Ticket": ticket_id, "Detailed": "true"}
    elif start_date and end_date and market:
        params = {
            "StartDate": start_date,
            "EndDate": end_date,
            "Market": _MARKET_IDS.get(market.lower(), market),
            "Detailed": "true",
        }
    else:
        raise BTGApiError("Forneça ticket_id OU start_date+end_date+market")

    r = requests.get(
        base_url,
        headers={"X-SecureConnect-Token": token},
        params=params,
        timeout=30,
    )
    try:
        return r.json()
    except Exception as exc:
        raise BTGApiError(f"Resposta inválida: {r.status_code}") from exc


def await_transaction_ticket_result( token: str, ticket_id: str, *, attempts: int = 10,
        interval: int = 30, test_env: bool = True) -> pd.DataFrame:
    """Espera a conclusão do ticket e devolve DataFrame com metadados.
    Args:
        token: Token de autenticação.
        ticket_id: ID do ticket.
        attempts: Número de tentativas.
        interval: Intervalo entre tentativas em segundos.
        test_env: Ambiente de teste (True) ou produção (False).

    Returns:
        DataFrame com o status detalhado das transações.

    Raises:
        BTGApiError: Se o ticket não for finalizado ou falhar.
        
    """

    cols = ["Status", "Ticket", "TradeId", "Env", "Msg"]
    results = pd.DataFrame(columns=cols)

    for i in range(attempts):
        data = get_submitted_transactions(token, ticket_id=ticket_id, test_env=test_env)
        trades_info = data["trades"]
        ticket_status = trades_info[0]["Status"].lower()

        # ambiente de produção pode ficar em pendente; aguardamos
        if ticket_status == "pendente":
            logger.info("Ticket %s pendente (%d/%d)", ticket_id, i + 1, attempts)
            time.sleep(interval)
            continue

        trades = trades_info[0]["Details"]["TicketDetalhesEquity"]
        for tr in trades:
            results.loc[len(results)] = [
                tr["stateItemFile"].lower(),
                ticket_id.lower(),
                tr["externalReference"],
                "test" if test_env else "prod",
                tr["mensagens"],
            ]
        return results

    raise BTGApiError("Ticket não finalizado no tempo limite")