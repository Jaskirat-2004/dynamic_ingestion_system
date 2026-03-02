import pandas as pd

def sample_generator(series):
    """
    Generate a sample of the series
    """
    
    series = series.dropna()
    sample_size = max(len(series)//100,min(100,len(series)))
    sample = series.sample(n=sample_size)

    return sample


def is_bool(series,threshold=0.9):
    """
    Check if the column is boolean
    """
    
    check = {"true","false","0","1","yes","no","y","n"}
    
    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()      
    )

    ratio = normalized.isin(check).mean()

    if ratio >= threshold:
        return True
         # If greater than threshold normalised the values to true and false and null

    return False

def is_int(series,threshold=0.9):
    """
    Check if the column is integer
    """

    normalized = pd.to_numeric(series,errors='coerce')

    ratio = normalized.notna().mean()

    if ratio < threshold:
        return False

    integer_ratio = (normalized.dropna() % 1 == 0).mean()

    return integer_ratio >= threshold

def is_float(series,threshold=0.9):
    """
    Check if the column is float
    """

    normalized = pd.to_numeric(series,errors='coerce')

    ratio = normalized.notna().mean()

    if ratio >= threshold:
        return True

    return False

def is_date(series,threshold=0.9):
    """
    Check if the column is date
    """
    normalized = pd.to_numeric(series,errors='coerce')
    ratio = normalized.notna().mean()
    if ratio > threshold:
        int_ratio = (normalized.dropna() % 1 == 0).mean()
        if int_ratio > threshold:
            date = pd.to_datetime(series,errors='coerce')
            date_ratio = date.notna().mean()
            if date_ratio >= threshold:
                return True
    return False
    

def column_type(df):
    """
    Infer the type of each column
    """

    types = {}

    for col in df.columns:

        sample = sample_generator(df[col])

        if sample.empty:
            types[col] = 'TEXT'

        elif is_bool(sample):
            types[col] = 'BOOLEAN'
        
        elif is_date(sample):
            types[col] = 'DATETIME'

        elif is_int(sample):
            types[col] = 'INTEGER'
        
        elif is_float(sample):
            types[col] = 'FLOAT'
        
        else:
            types[col] = 'TEXT'

    return types




def date_conversion(df,head_size=100,threshold = 0.8):

    for col in df.columns:

        if df[col].dtype in ['object','int64','float64']:
            sample = df[col].dropna().head(head_size)
            
            if sample.empty:
                continue

            try:
                converted = pd.to_datetime(sample,errors='coerce')
                success_rate = converted.notna().sum()/len(sample)

                if success_rate >= threshold:
                    df[col] = pd.to_datetime(df[col],errors='coerce')

            except Exception as e:
                continue
    return df


def infer_schema(df):

    # df = date_conversion(df)
    
    schema_dict = df.dtypes.to_dict()
    
    dtype_map = {
        'object': 'TEXT',
        'int64': 'BIGINT',
        'int32': 'INTEGER',
        'float64': 'DOUBLE PRECISION',
        'float32': 'REAL',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP',
        'timedelta64[ns]': 'INTERVAL',
        'category': 'TEXT'
    }
    
    final_schema = {}
    for col, dtype in schema_dict.items():
        dtype_str = str(dtype)
        final_schema[col] = dtype_map.get(dtype_str, 'TEXT')
    
    return final_schema







