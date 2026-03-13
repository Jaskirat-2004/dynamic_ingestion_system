"""
THIS HAS ALL THE REQUIRED SQL QUERIES
"""

def create_table_query(schema:dict,table_name:str):
    """
    THIS FUNCTION TAKES A DICTIONARY OF COLUMN NAMES AND DATA TYPES
    AND A TABLE NAME AS INPUT AND RETURNS A CREATE TABLE QUERY
    """

    columns = []
    for col,dtype in schema.items():
        columns.append(f'"{col}" {dtype}')
    
    columns_str = ",\n".join(columns)

    querry = f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    ({columns_str})
    """

    return querry

def list_tables_query(schema = "public"):
    """
    THIS FUNCTION TAKES A SCHEMA NAME AS INPUT AND RETURNS A LIST OF TABLES IN THAT SCHEMA
    """
    # used parameterized query to prevent sql injection
    
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = %s
    """
    values = (schema,)
    # pass as tuple

    return query,values

def list_columns_query(table_name:str):
    """
    THIS FUNCTION TAKES A TABLE NAME AS INPUT AND RETURNS A LIST OF COLUMNS IN THAT TABLE
    """

    query = """
    SELECT column_name,data_type
    FROM information_schema.columns
    WHERE table_name = %s
    """
    values = (table_name,)

    return query,values





