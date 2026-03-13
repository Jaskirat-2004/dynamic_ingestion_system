from fastapi import FastAPI , Request , UploadFile, File, Form

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#############################################################################

import uuid
import os
import json
import pandas as pd

#############################################################################

from app.ingestion.reading import read_file,load_session_df
from app.ingestion.infer_schema import column_types
from app.ingestion.enforce import enforce_types

from app.db.sql_query import create_table_query,list_tables_query
from app.db.query_execution import run_query
from app.db.push import push_to_db

#############################################################################

if not os.path.exists("temp"):
    os.makedirs("temp")

app = FastAPI()

# CREATE JINJA INSTANCE
templates = Jinja2Templates(directory="templates")

# CONNECT STATIC FILES LIKE TEMPLATES DIRECTORY
app.mount("/static",StaticFiles(directory="static"),name="static")

# THIS IS ROOT 
@app.get('/')
def root():
    return {"OWNER":"JASKIRAT",
            "PROJECT":"DATA INGESTION SYSTEM"}

# THIS DISPLAYS THE UPLOAD PORTAL
@app.get("/upload",response_class=HTMLResponse)
def show_form(request: Request):
    
    # FETCHING THE TABLES FROM THE DATABASE
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
    ):

    errors = None

    if table == "__new__":
        table_name = newTable
    else:
        table_name = table

    try:
        df = read_file(file.file,file.filename)
        SCHEMA = column_types(df)

        # CREATING UNIQUE SESSION ID
        session_id = str(uuid.uuid4())

        # SAVING DF IN SESSION
        df.to_pickle(f"temp/{session_id}.pkl")

        # SAVING SCHEMA TEMPORARILY
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

@app.post("/confirm-schema")
async def confirm_schema(request:Request):

    form = await request.form()

    session_id = form.get("session_id")
    table_name = form.get("table_name")
    primary_key = form.get("primary_key")

    validated_schema = {}

    for key,value in form.items():
        if key.startswith("type_"):
            column = key.replace("type_","")
            validated_schema[column] = value

    errors = None

    try:
        # READING THE DF
        df = load_session_df(session_id)

        # ENFORCING THE SCHEMA
        df = enforce_types(df,validated_schema)
        
        # CREATING THE TABLE
        create_table = create_table_query(validated_schema,table_name)
        run_query(create_table)

        # INSERTING THE DATA
        push_to_db(df,table_name)

    except Exception as e:
        errors = str(e)
    
    # cleanup
    os.remove(f"temp/{session_id}.pkl")
    os.remove(f"temp/{session_id}_schema.json")

    if errors:
        return templates.TemplateResponse(
            "result.html",
            {
                "request":request,
                "error": errors
            }
        )
    
    else:
        return templates.TemplateResponse(
            "result.html",
            {
                "request":request,
                "l": len(df),
                "cols": list(df.columns),
                "table_name":table_name,
                "error": errors
            }
        )

       