import pandas as pd

BOOL_CHECK = {"true","false","0","1","yes","no","y","n"}

TYPE_PRIORITY = {
        'BOOLEAN':1,
        'INTEGER':2,
        'FLOAT':3,
        'DATE':4,
        'TEXT':5
    }

def sample_generator(series):
    """
    Generate a sample of the series
    """
    
    series = series.dropna()
    sample_size = max(len(series)//100,min(100,len(series)))
    sample = series.sample(n=sample_size)

    return sample

def infer_schema(series,threshold=0.95):
    
    scores = {}

    # TEXT
    if series.empty:
        return 'TEXT'
    
    # BOOLEAN
    normalized_str = series.astype(str).str.strip().str.lower()
    boolean_ratio = normalized_str.isin(BOOL_CHECK).mean()
    scores['BOOLEAN'] = boolean_ratio
    
    # DATE
    date = pd.to_datetime(series,errors='coerce')
    date_ratio = date.notna().mean()
    scores['DATE'] = date_ratio

    # NUMERIC
    numeric = pd.to_numeric(series,errors='coerce')
    numeric_ratio = numeric.notna().mean()
    
    if numeric_ratio > 0:
        scores['FLOAT'] = numeric_ratio
        integer_ratio = (numeric % 1 == 0).mean()
        if integer_ratio > 0:
            scores['INTEGER'] = integer_ratio
    else:
        scores['FLOAT'] = 0
        scores['INTEGER'] = 0


    best_match = max(
        scores,
        key = lambda x: (scores[x],-TYPE_PRIORITY[x])
        #  Negative sign is used because we want to prioritize the lower value
    )

    if scores[best_match] >= threshold:
        return best_match

    return 'TEXT'

def column_types(df):
    """
    THIS FUNCTION TAKES A DATAFRAME AS INPUT AND RETURNS A DICTIONARY OF COLUMN NAMES AND DATA TYPES
    """

    types = {}

    for col in df.columns:
        
        sample = sample_generator(df[col])
        types[col] = infer_schema(sample)
    
    return types




