
from app.ingestion.reading import read_file

from app.db.sql_query import create_table_query,list_tables_query

from app.db.query_execution import run_query

from app.ingestion.infer_schema import sample_generator,column_types

import pandas as pd

table_name = "hello"
schema = {
    "name":"TEXT",
    "age":"INTEGER",
    "salary":"DOUBLE PRECISION",
    "is_student":"BOOLEAN",
    "created_at":"TIMESTAMP"
}


df = read_file(r"C:\Users\8242K\Desktop\WFM\Pan India\TL-Wise Attrition\Dumps\head_count_job.csv","head_count_job.csv")
# s = df.dtypes.to_dict()
# print(s)

# Schema = infer_schema(df)
# print(Schema)

# q = create_table_query(schema,table_name)
# print(q)

# create_table(q)

# print(df.head(15))
# print(df.sample(100))

# print(column_type(df))

# ls= [0,1,2,5,2,3,5,6,1,3,5.6,6.4,"frch",True,False]

# print(is_bool(df[i]))

# a = column_types(df)
# print(a)

# b = create_table_query(a,"hc")
# print(b)

# run_query(b)

a,b = list_tables_query()
c = run_query(a,b,fetch=True)
print(c)
q = """
SELECT * FROM users;
"""
r = run_query(q,fetch=True)
print(r)

hv = [row[0] for row in r]
print(hv)


