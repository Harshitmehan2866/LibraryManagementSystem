import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=LibraryDB;"
        "UID=SA;"
        "PWD=harshit@9420;"
        "TrustServerCertificate=yes;"
    )
    print("Connection successful!")
except Exception as e:
    print("Error:", e)
