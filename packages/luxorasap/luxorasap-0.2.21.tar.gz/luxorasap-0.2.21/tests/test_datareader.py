"""
Teste rápido (integração) do LuxorQuery.

• Requer que AZURE_STORAGE_CONNECTION_STRING esteja definido e que a
  tabela/arquivo da série solicitada exista no data lake.

Para rodar:

    # (na raiz do repositório)
    make install      # ou  pip install -e ".[dev,datareader]"
    export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=...;AccountKey=..."
    pytest -q

Se a variável não estiver presente, o teste será automaticamente ignorado.
"""

# tests/test_datareader.py
import os
from pathlib import Path
import datetime as dt

import pandas as pd
import pytest
from dotenv import load_dotenv

# ── 1. Carrega variáveis do .env na raiz do projeto ───────────────
ROOT = Path(__file__).resolve().parents[1]  # .../luxor-asap
load_dotenv(ROOT / ".env")

# ── 2. Verifica se a credencial Azure está presente ───────────────
AZURE_ENV_KEY = "AZURE_STORAGE_CONNECTION_STRING"

@pytest.mark.skipif(
    os.getenv(AZURE_ENV_KEY) is None,
    reason=f"{AZURE_ENV_KEY} não definida – teste de integração pulado",
)
def test_get_prices_returns_non_empty_dataframe():
    """
    Busca uma janela curta de preços usando LuxorQuery e checa estrutura mínima.
    """
    from luxorasap.datareader import LuxorQuery

    lq = LuxorQuery()

    df = lq.get_prices(
        "aapl us equity",
        previous_date=dt.date(2024, 1, 2),
        recent_date=dt.date(2024, 1, 10),
    )

    # 1) Deve retornar DataFrame não vazio
    assert not df.empty, "DataFrame veio vazio – verifique ticker/datas"
    
    # 2) Índice datetime e pelo menos uma coluna numérica
    assert df.select_dtypes("number").shape[1] > 0
    assert df.select_dtypes("datetime64").shape[1] > 0