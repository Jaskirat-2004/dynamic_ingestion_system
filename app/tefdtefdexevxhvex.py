import pandas as pd

# df = pd.read_csv(r"C:\Users\8242K\Desktop\WFM\Pan India\TL-Wise Attrition\Dumps\head_count_job.csv")
# s = df.dtypes.to_dict()
# print(s)

# # SCHEMA = infer_schema(df)
# # print(SCHEMA)

# cols = [f"{col} {d}" for col,d in s.items()]

# print(cols)


# col_str = ",".join(cols)
# print(col_str)
    

# l = ["gs","DDad","dad","wgev","wewefw"]

# print(l)

# print("\n".join(l))

l = [1,2,3,4,5,6,7,8,9,10,"D","eded","edded","edded"]

l = pd.to_numeric(l,errors='coerce')
print(l)