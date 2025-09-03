import pyodbc
driver = "{ODBC Driver 17 for SQL Server}"

def get_connection(connectionString: str) -> pyodbc.Connection:
    parts = dict(part.split("=") for part in connectionString.split(";"))
    server = parts["Data Source"]
    database = parts["Initial Catalog"]
    username = parts["User ID"]
    password = parts["Password"]
    new_connection_string= rf"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(new_connection_string)
    return connection 