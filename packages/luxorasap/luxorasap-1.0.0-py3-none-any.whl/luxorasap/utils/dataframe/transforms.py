import pandas as pd
import gc
from pandas.api.types import is_object_dtype, is_string_dtype


def text_to_lowercase_inplace(df: pd.DataFrame, cols: list[str]) -> None:
    """
    Converte para lower+strip apenas as células que são str.
    Não tenta aplicar `.str` se a coluna (ou célula) não for string.
    Opera in-place; não devolve nada.
    """
    for col in cols:
        # Precisa ser coluna potencialmente textual
        if not (is_object_dtype(df[col]) or is_string_dtype(df[col])):
            continue

        # Cria máscara com valores realmente str (ignora NaN, ints, decimals…)
        mask = df[col].apply(lambda x: isinstance(x, str))

        if mask.any():                              # só se houver algo a tratar
            df.loc[mask, col] = (
                df.loc[mask, col]
                  .str.lower()
                  .str.strip()
            )


def persist_column_formatting(df: pd.DataFrame,
        columns_to_persist_override: set | None = None) -> pd.DataFrame:
    if columns_to_persist_override is None:
        columns_to_persist_override = set()

    cols_keep_case = {
        "Name", "Class", "Vehicles", "Segment"
    }.union(columns_to_persist_override)

    # Só colunas objeto/string candidatas
    candidate_cols = [
        c for c in df.columns
        if c not in cols_keep_case and
           (df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c]))
    ]

    text_to_lowercase_inplace(df, candidate_cols)

    return df  # mesma referência; alterações foram in-place


def prep_for_save(
    df: pd.DataFrame,
    *,
    index: bool = False,
    index_name: str = "index",
    normalize: bool = False,
):
    if index:
        name = df.index.name or index_name
        df = df.reset_index().rename(columns={"index": name})
    return persist_column_formatting(df) if normalize else df


def astype_str_inplace(df: pd.DataFrame, *, gc_every: int = 3) -> None:
    """
    Converte TODAS as colunas para string sem duplicar o DataFrame completo.
    Em cada passo:
      • cria uma nova Series (coluna convertida)
      • substitui a antiga
      • libera memória da coluna anterior
    Isso mantém o pico de RAM ≤ tamanho da maior coluna.
    """
    for i, col in enumerate(df.columns):
        df[col] = df[col].astype(str)

        # opcional: força coleta de lixo a cada N colunas
        if (i + 1) % gc_every == 0:
            gc.collect()