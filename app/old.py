import pandas as pd


############################################################################
############################################################################


from fastapi import FastAPI , Request , UploadFile, File, Form

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#############################################################################

import uuid
import os
import json

#############################################################################

from app.ingestion.reading import read_file
from app.ingestion.infer_schema import column_types
from app.ingestion.enforce import enforce_types

from app.db.sql_query import create_table_query,list_tables_query
from app.db.query_execution import run_query
from app.db.push import push_to_db

#############################################################################

if not os.path.exists("temp"):
    os.makedirs("temp")

app = FastAPI()

# create jinja instance
templates = Jinja2Templates(directory="templates")

#connect static files like templates directory
app.mount("/static",StaticFiles(directory="static"),name="static")

# THIS IS ROOT 
@app.get('/')
def root():
    return {"OWNER":"JASKIRAT",
            "PROJECT":"DATA INGESTION SYSTEM"}

# THIS DISPLAYS THE UPLOAD PORTAL
@app.get("/upload",response_class=HTMLResponse)
def show_form(request: Request):
    
    # Fetching the tables from the database
    table_query,db_schema = list_tables_query() 
    tables = run_query(table_query,values = db_schema,fetch=True)
    flat_tables = [table[0] for table in tables]

    return templates.TemplateResponse(
        "index.html",
        {"request":request,
         "tables":flat_tables}
    )


@app.post("/upload-preview",response_class=HTMLResponse)
def upload_preview(
    request: Request,
    file: UploadFile = File(...),
    table:str = Form(...),
    newTable:str = Form(None)
    ) :

    errors = None

    if table == "__new__":
        table_name = newTable
    else:
        table_name = table

    try:
        df = read_file(file.file,file.filename)
        SCHEMA = column_types(df)

        # create unique session id
        session_id = str(uuid.uuid4())

        # save df in session
        df.to_pickle(f"temp/{session_id}.pkl")

        # save schema temporarily
        with open(f"temp/{session_id}_schema.json","w") as f:
            json.dump(SCHEMA,f)
        
        return templates.TemplateResponse(
            "upload_preview.html",
            {
                "request":request,
                "schema":SCHEMA,
                "table_name":table_name,
                "session_id":session_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "error": errors
            }
        )

    except Exception as e:
        errors = str(e)

        return templates.TemplateResponse(
            "upload_preview.html",
            {
                "request":request,
                "error": errors
            }
        )

# POST METHOD THAT OPENS WHEN FILE IS UPLODED
@app.post("/uploaded",response_class=HTMLResponse)
def show_name(
    request: Request,
    file: UploadFile = File(...),
    table:str = Form(...),
    newTable:str = Form(None)
    ) :

    errors = None

    if table == "__new__":
        table_name = newTable
    else:
        table_name = table

    try:
        # Reading the file
        df = read_file(file.file,file.filename)
        
        # Inferring the schema
        SCHEMA = column_types(df)

        # Creating the table
        create_table = create_table_query(SCHEMA,table_name)
        run_query(create_table)

        # Enforcing The SCHEMA
        df = enforce_types(df,SCHEMA)

        # Inserting the data
        push_to_db(df,table_name)

    except Exception as e:
        errors = str(e)

    if errors:
         return templates.TemplateResponse(
            "result.html",
            {
                "request":request,
                "filename": None,
                "content_type": file.content_type,
                "error": errors
            }
        )
    
    else:

        return templates.TemplateResponse(
            "result.html",
            {
                "request":request,
                "filename": file.filename,
                "content_type": file.content_type,
                "error": errors
            }
        )





############################################################################
############################################################################
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







