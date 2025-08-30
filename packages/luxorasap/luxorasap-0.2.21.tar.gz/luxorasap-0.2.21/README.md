# 🧠 LuxorASAP

**Luxor Automatic System for Assets and Portfolios** é o toolbox oficial da Luxor para automação de pipelines de dados, integração com APIs financeiras e gerenciamento eficiente de dados patrimoniais no Azure.

Projetado para ser rápido, reutilizável e seguro, este pacote unifica a ingestão, leitura e transformação de dados utilizados nas análises e marcações do time de investimentos.

---

## 🚀 Funcionalidades

- 📡 Integração com a API de relatórios e boletas do BTG Pactual
- 🗂️ Carregamento padronizado de arquivos (Excel, Parquet, Blob)
- 💾 Escrita incremental e segura no ADLS (Azure Blob Storage)
- 📊 Análises de preço, retorno e risco com API de consulta (`LuxorQuery`)
- 🔗 Modularidade entre `btgapi`, `datareader`, `ingest`, `utils`

---

## 🧩 Estrutura do Projeto

```
luxor-asap/
├── src/luxorasap/
│   ├── btgapi/          # Integração com BTG Pactual
│   ├── datareader/      # Interface de leitura e análise de dados
│   ├── ingest/          # Carga de dados no ADLS
│   └── utils/           # Funções auxiliares (parquet, dataframe)
└── tests/               # Testes automatizados com Pytest
```

---

## 📚 Documentação

A documentação externa completa está disponível em:

[![Docs](https://img.shields.io/badge/docs-online-blue)](https://luxorinvestimentos.github.io/luxorasap-docs/)

---

## 🔧 Requisitos

- Python 3.9+
- Azure Blob Storage configurado
- Variáveis de ambiente via `.env` (ou passadas manualmente):

```bash
AZURE_STORAGE_CONNECTION_STRING=...
BTG_CLIENT_ID=...
BTG_CLIENT_SECRET=...
```

---

## 📦 Instalação

Para instalar localmente:

```bash
pip install -e .
```

Ou via PyPI:

```bash
pip install luxor-asap
```

---

## 🧪 Testes

```bash
pytest -v
```

---

## 📄 Licença

Projeto de uso interno do Luxor Group. Todos os direitos reservados.