from io import StringIO
from app.db.connection import get_conn

class InsertException(Exception):
    pass

def push_to_db(df,table_name):
    """
    THIS FUNCTION TAKES A DATAFRAME AND A TABLE NAME AS INPUT
    AND PUSHES THE DATA TO THE DATABASE
    """

    conn = get_conn()
    cur = conn.cursor()

    try:

        buffer = StringIO()
        df.to_csv(buffer,index=False,header=False,na_rep='\\N')
        buffer.seek(0)

        columns = []
        for col in df.columns:
            columns.append(f'"{col}"')
        columns_str = ",".join(columns)

        query = f"""
        COPY {table_name} ({columns_str})
        FROM STDIN WITH CSV NULL '\\N'
        """

        cur.copy_expert(query,buffer)

    except Exception as e:
        conn.rollback()
        raise InsertException(str(e))

    else:
        conn.commit()
        print("<"*10,"DATA PUSHED",">"*10)

    finally:
        cur.close()
        conn.close()


