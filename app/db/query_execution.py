"""
THIS FILE CONTAINS THE REQUIRED FUNCTIONS TO EXECUTE QUERIES
"""

class QueryExecutionError(Exception):
    pass

from app.db.connection import get_conn

def run_query(query,values=None,fetch=False):
    """
    Execute any SQL query safely.
    
    Parameters:
    - query (str): SQL query to execute
    - values (tuple/list): parameters for query
    - fetch (bool): if True, returns results (for SELECT)
    
    Returns:
    - list of tuples if fetch = True
    - None otherwise

    """

    conn = get_conn()
    cursor = conn.cursor()
    result = None

    try:
        if values:
            cursor.execute(query,values)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()

    except Exception as e:
        print("*"*10,"QUERY EXECUTION FAILED","*"*10)
        raise QueryExecutionError(str(e))

    else:
        print("*"*10,"QUERY EXECUTED SUCCESSFULLY","*"*10)

    finally:
        cursor.close()
        conn.close()

    return result if result else []

