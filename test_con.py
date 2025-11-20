import pyodbc

conn_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=ibrary-sql-server.database.windows.net;"
    "DATABASE=librarydb;"
    "UID=harshitmehan;"
    "PWD=harshit@9420;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

try:
    conn = pyodbc.connect(conn_string)
    print("Connected successfully!")
except Exception as e:
    print("Error:", e)
