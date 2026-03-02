import pandas as pd

def enforce_types(df, inferred_types):
    for col, dtype in inferred_types.items():

        if dtype == 'INTEGER':
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        elif dtype == 'FLOAT':
            df[col] = pd.to_numeric(df[col], errors='coerce')

        elif dtype == 'BOOLEAN':
            df[col] = df[col].astype(str).str.strip().str.lower()
            df[col] = df[col].map({
                'true': True, '1': True, 'yes': True, 'y': True,
                'false': False, '0': False, 'no': False, 'n': False
            })

        elif dtype == 'DATE':
            df[col] = pd.to_datetime(df[col], errors='coerce')

        else:
            df[col] = df[col].astype(str)

    return df