import pandas as pd

class FileTypeError(Exception):
    pass

class EmptyDfError(Exception):
    pass

def read_file(file,filename:str):
    filename = filename.lower().strip()
        
    if filename.endswith('.xlsx'):
        df = pd.read_excel(file)
    elif filename.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        raise FileTypeError(f"ONLY .csv or .xlsx FILES ALLOWED - {filename}")
    
    if df.empty:
        raise EmptyDfError("THE FILE IS EMPTY")

    return df  

def load_session_df(session_id: str):
    return pd.read_pickle(f"temp/{session_id}.pkl")
