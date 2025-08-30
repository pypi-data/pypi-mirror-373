"""Wrapper para as APIs do BTG Pactual."""

from .auth import get_access_token, BTGApiError
from .reports import request_portfolio, await_report_ticket_result, process_zip_to_dfs, request_investors_transactions_report, request_fundflow_report
from .trades import submit_offshore_equity_trades, await_transaction_ticket_result

__all__ = [
    "BTGApiError",
    "get_access_token",
    "request_portfolio",
    "await_report_ticket_result",
    "submit_offshore_equity_trades",
    "await_transaction_ticket_result",
    "process_zip_to_dfs",
    "request_investors_transactions_report",
    "request_fundflow_report",
]