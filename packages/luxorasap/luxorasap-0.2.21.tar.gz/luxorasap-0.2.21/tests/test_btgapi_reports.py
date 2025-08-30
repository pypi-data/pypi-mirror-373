import datetime as dt, io, json, zipfile
import pandas as pd
import pytest

from luxorasap.btgapi.reports import (
    request_portfolio,
    await_report_ticket_result,
    process_zip_to_dfs,
    check_report_ticket,
    request_fundflow_report,
)

_TICKET_URL = "https://funds.btgpactual.com/reports/Ticket"
_POST_URL   = "https://funds.btgpactual.com/reports/Portfolio"
_FUNDFLOW_URL = "https://funds.btgpactual.com/reports/RTA/FundFlow"

_TOKEN = "dummy-token"

def test_request_portfolio_returns_ticket(requests_mock):
    requests_mock.post(_POST_URL, json={"ticket": "ABC"})
    tk = request_portfolio("tok", "FUND", dt.date(2025,1,1), dt.date(2025,1,31))
    assert tk == "ABC"

def test_await_ticket_inline_zip(requests_mock, monkeypatch):
    # 1ª chamada: ainda processando   2ª: devolve ZIP binário
    # Explicando o que requests_mock faz:
    # 
    requests_mock.get(_TICKET_URL, [
        {"json": {"result": "Processando"}},
        {"content": b"ZIP!"},
    ])
    monkeypatch.setattr("time.sleep", lambda *_: None)
    out = await_report_ticket_result("tok", "ABC", attempts=2, interval=0)
    assert out == b"ZIP!"

def test_await_ticket_via_urldownload(requests_mock, monkeypatch):
    dl_url = "https://download/file.zip"
    # 1ª chamada ao ticket devolve JSON com UrlDownload
    requests_mock.get(_TICKET_URL, json={"result": json.dumps({"UrlDownload": dl_url})})
    requests_mock.get(dl_url, content=b"ZIP2", headers={"Content-Type": "application/zip"})
    monkeypatch.setattr("time.sleep", lambda *_: None)
    out = await_report_ticket_result("tok", "XYZ", attempts=1)
    assert out == b"ZIP2"


def test_process_zip_to_dfs():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        df = pd.DataFrame({"x": [1]})
        zf.writestr("data.csv", df.to_csv(index=False))
    dfs = process_zip_to_dfs(buf.getvalue())
    assert dfs["data.csv"].iloc[0, 0] == 1
    
    
def test_process_zip_latin1_csv():
    import io, zipfile, pandas as pd
    from luxorasap.btgapi.reports import process_zip_to_dfs

    df_src = pd.DataFrame({"nome": ["ação", "æøå"]})
    csv_latin1 = df_src.to_csv(index=False, encoding="latin1")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("dados.csv", csv_latin1)

    dfs = process_zip_to_dfs(buf.getvalue())
    assert dfs["dados.csv"].equals(df_src)
    

def test_request_fundflow_report_success(requests_mock):
    """POST devolvendo ticket e corpo montado corretamente."""
    start, end = dt.date(2025, 5, 4), dt.date(2025, 6, 4)
    fund_name   = "luxor lipizzaner fia"
    expected_id = "TCK-123"

    # valida corpo enviado
    def _match(request):
        payload = request.json()
        c = payload["contract"]
        assert c["startDate"] == f"{start}T00:00:00Z"
        assert c["endDate"]   == f"{end}T00:00:00Z"
        assert c["fundName"]  == fund_name
        assert c["dateType"]  == "LIQUIDACAO"
        return True

    requests_mock.post(
        _FUNDFLOW_URL,
        additional_matcher=_match,
        json={"ticket": expected_id},
        status_code=200,
    )

    ticket = request_fundflow_report(
        _TOKEN, start, end, fund_name=fund_name
    )
    assert ticket == expected_id
    

def test_check_report_ticket_returns_dataframe(requests_mock):
    """GET devolvendo JSON-list deve virar DataFrame."""
    ticket_id   = "TCK-LIST"
    sample_rows = [
        {"customerName": "A", "valueTotal": 1_000},
        {"customerName": "B", "valueTotal": 2_000},
    ]

    # qualquer query param é aceito; podemos validar se quiser via matcher
    requests_mock.get(
        _TICKET_URL,
        json={"result": sample_rows},
        status_code=200,
    )

    df = check_report_ticket(_TOKEN, ticket_id)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"customerName", "valueTotal"}
    
    
def test_await_report_ticket_polls_until_ready(requests_mock, monkeypatch):
    """Primeira chamada ‘Processando’ → segunda retorna lista."""
    ticket_id   = "TCK-POLL"
    ready_rows  = [{"x": 1}]

    # sequencia de respostas: processamento → pronto
    requests_mock.get(
        _TICKET_URL,
        [
            {"json": {"result": "Processando"}, "status_code": 200},
            {"json": {"result": ready_rows},    "status_code": 200},
        ],
    )

    # evita atraso real de sleep
    monkeypatch.setattr("luxorasap.btgapi.reports.time.sleep", lambda *_: None)

    df = await_report_ticket_result(_TOKEN, ticket_id, attempts=2, interval=0)
    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0, 0] == 1