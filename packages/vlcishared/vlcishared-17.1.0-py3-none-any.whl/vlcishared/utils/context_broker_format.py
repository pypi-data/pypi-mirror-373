from pandas import DataFrame


CARACTERES_PROHIBIDOS_CONTEXT_BROKER = {
    '>': '[', '<': ']', '‘': '´', '“': '´',
    '=': '-', ';': ',', '(': '[', ')': ']',
    "'": '´',
}


def reemplazar_caracteres_prohibidos_context_broker(df: DataFrame) -> DataFrame:
    df = df.copy()
    
    for columna in df.columns:
        if df[columna].dtype == object:
            for caracter, sustituto in CARACTERES_PROHIBIDOS_CONTEXT_BROKER.items():
                df[columna] = df[columna].str.replace(caracter, sustituto, regex=False)
    return df
