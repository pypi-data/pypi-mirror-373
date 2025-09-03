import sqlite3
import psycopg2
import pymysql
import pyodbc  # For Azure SQL


def get_sql_server_driver():
    """Return the best available SQL Server ODBC driver."""
    drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
    if not drivers:
        raise RuntimeError("❌ No SQL Server ODBC driver found. Please install one (e.g. ODBC Driver 17/18).")
    return drivers[-1]  # Pick the latest available driver


def connect(db_type, **kw):
    # SQLite
    if db_type == "sqlite":
        conn = sqlite3.connect(kw.get("database", ":memory:"))
        print(f"✅ SQLite connection established to database: {kw.get('database', ':memory:')}")
        return conn

    # PostgreSQL
    if db_type == "postgres":
        if "url" in kw:
            conn = psycopg2.connect(kw["url"])
            print("✅ PostgreSQL connection established using URL")
            return conn
        conn = psycopg2.connect(
            host=kw.get("host", "localhost"),
            user=kw["user"],
            password=kw["password"],
            dbname=kw["database"],
            port=kw.get("port", 5432)
        )
        print(f"✅ PostgreSQL connection established to database: {kw['database']} on host: {kw.get('host', 'localhost')}")
        return conn

    # MySQL
    if db_type == "mysql":
        conn = pymysql.connect(
            host=kw.get("host", "localhost"),
            user=kw["user"],
            password=kw["password"],
            database=kw["database"],
            port=kw.get("port", 3306)
        )
        print(f"✅ MySQL connection established to database: {kw['database']} on host: {kw.get('host', 'localhost')}")
        return conn

    # Azure SQL (with auto-detected driver)
    if db_type == "azure_sql":
        driver = kw.get("driver", get_sql_server_driver())
        conn = pyodbc.connect(
            driver=driver,
            server=kw["server"],
            database=kw["database"],
            uid=kw["user"],
            pwd=kw["password"]
        )
        print(f"✅ Azure SQL connection established to {kw['database']} on {kw['server']} using {driver}")
        return conn

    raise ValueError(f"❌ Unsupported database type: {db_type}")
