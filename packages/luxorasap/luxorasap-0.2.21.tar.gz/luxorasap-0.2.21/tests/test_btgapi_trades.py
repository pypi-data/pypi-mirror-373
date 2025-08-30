import pandas as pd
import pytest
from types import SimpleNamespace
from luxorasap.btgapi.trades import (
    submit_offshore_equity_trades,
    get_submitted_transactions,
    await_transaction_ticket_result,
)

_SUBMIT_URL = "https://funds-uat.btgpactual.com/offshore/TradeOffShore/Equity"
_TICKET_URL = "https://funds-uat.btgpactual.com/offshore/Ticket"

def test_submit_trades_returns_ticket(requests_mock):
    requests_mock.post(_SUBMIT_URL, status_code=201, json={"ticket": "T1"})
    ticket = submit_offshore_equity_trades("tok", trades=[{}], test_env=True)
    assert ticket == "T1"

def test_get_submitted_transactions_ok(requests_mock):
    payload = {"trades":[{"Status":"OK","Details":{"TicketDetalhesEquity":[]}}]}
    requests_mock.get(_TICKET_URL, json=payload)
    data = get_submitted_transactions("tok", ticket_id="T1", test_env=True)
    assert data["trades"][0]["Status"] == "OK"

def test_await_transaction_ticket_result(requests_mock, monkeypatch):
    details = [
        {
            "stateItemFile":"processada",
            "externalReference":"ID123",
            "mensagens":"ok"
        }
    ]
    payload = {"trades":[{"Status":"Processado","Details":{"TicketDetalhesEquity":details}}]}
    requests_mock.get(_TICKET_URL, json=payload)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    df = await_transaction_ticket_result("tok", "T1", attempts=1, test_env=True)
    assert isinstance(df, pd.DataFrame)
    assert (df["TradeId"] == "ID123").all()