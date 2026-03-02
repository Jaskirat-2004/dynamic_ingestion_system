import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def get_conn():
    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        port = os.getenv("DB_PORT")
    )

    print("*"*10,"Connected to DB","*"*10)
    
    return conn
