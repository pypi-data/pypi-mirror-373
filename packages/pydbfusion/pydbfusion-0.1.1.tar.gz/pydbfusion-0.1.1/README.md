#pydbfusion

A minimal universal database connection library for **SQLite, PostgreSQL, MySQL and Azure SQL database**.  
One simple function to connect to multiple databases without worrying about different drivers.


First, install the library.

```bash
pip install pydbfusion
```

How to use this library and connect to different databases with examples:
1.Import the connect function.

from pydbfusion import connect



2.To Connect to SQLite:
conn = connect(
    "sqlite",
    database="my_database.db"  # optional, defaults to ":memory:"
)

3.Connect to PostgreSQL

Option A: Using individual parameters

conn = connect(
    "postgres",
    host="localhost",
    user="postgres",
    password="mypassword",
    database="testdb",
    port=5432  # optional, default is 5432
)

Option B: Using a URL

conn = connect(
    "postgres",
    url="postgresql://username:password@host:port/database"
)

4.Connect to MySQL
conn = connect(
    "mysql",
    host="localhost",
    user="root",
    password="mypassword",
    database="testdb",
    port=3306  # optional, default is 3306
)

5.Connect to Azure SQL database
conn = connect(
    "azure_sql",
    server=server,
    database=database,
    user=user,
    password=password
    )