from fastapi import FastAPI , Request , UploadFile, File, Form

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#############################################################################

from app.ingestion.reading import read_file
from app.ingestion.infer_schema import column_types
from app.ingestion.enforce import enforce_types

from app.db.sql_query import create_table_query,list_tables_query
from app.db.query_execution import run_query
from app.db.push import push_to_db

#############################################################################

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

       