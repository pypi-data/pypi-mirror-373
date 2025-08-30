import os
import requests
from dotenv import load_dotenv
from loguru import logger

__all__ = ["BTGApiError", "get_access_token"]


class BTGApiError(Exception):
    """Erro genérico da API do BTG."""


def get_access_token(*, client_id=None, client_secret=None, test_env: bool = True,
                    timeout: int = 20) -> str:
    """Obtém JWT válido por ~1 h para autenticação nas APIs BTG.
    Args:
        client_id: ID do cliente (opcional, lê de env var se None).
        client_secret: Segredo do cliente (opcional, lê de env var se None).
        test_env: Ambiente de teste (True) ou produção (False).
        timeout: Timeout da requisição em segundos.

    Returns:
        Token de acesso.

    Raises:
        BTGApiError: Se as credenciais não estiverem disponíveis ou a requisição falhar.
    """

    if not client_id or not client_secret:
        load_dotenv()
        client_id = os.getenv("BTG_CLIENT_ID")
        client_secret = os.getenv("BTG_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise BTGApiError("BTG_CLIENT_ID ou BTG_CLIENT_SECRET não definidos no ambiente")

    url = (
        "https://funds-uat.btgpactual.com/connect/token"
        if test_env
        else "https://funds.btgpactual.com/connect/token"
    )

    resp = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=timeout,
    )

    if resp.ok:
        token = resp.json().get("access_token")
        len_token = len(token) if token else None
        logger.info(f"Token BTG obtido (len={len_token})")
        return token or ""
    raise BTGApiError(f"Falha ao autenticar: HTTP {resp.status_code} – {resp.text}")