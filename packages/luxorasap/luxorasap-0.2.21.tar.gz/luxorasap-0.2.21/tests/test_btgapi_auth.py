import pytest
from luxorasap.btgapi.auth import get_access_token, BTGApiError

def test_get_access_token_ok(requests_mock, monkeypatch):
    url = "https://funds-uat.btgpactual.com/connect/token"
    requests_mock.post(url, json={"access_token": "TOKEN"})
    monkeypatch.setenv("BTG_CLIENT_ID", "id")
    monkeypatch.setenv("BTG_CLIENT_SECRET", "secret")
    assert get_access_token(test_env=True) == "TOKEN"

def test_get_access_token_fail(requests_mock, monkeypatch):
    url = "https://funds-uat.btgpactual.com/connect/token"
    requests_mock.post(url, status_code=400, text="bad")
    monkeypatch.setenv("BTG_CLIENT_ID", "id")
    monkeypatch.setenv("BTG_CLIENT_SECRET", "secret")
    with pytest.raises(BTGApiError):
        get_access_token(test_env=True)
