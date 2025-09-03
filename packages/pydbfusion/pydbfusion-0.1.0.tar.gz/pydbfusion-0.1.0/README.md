# dbconnect

A minimal universal database connection library for **SQLite, PostgreSQL, MySQL and Azure SQL database.**.  
One simple function to connect to multiple databases without worrying about different drivers.


Install the library

```bash
pip install pydbconnect
```

How to use this library and connect to different databases with examples:
1.Import the connect function.

from pydbconnect import connect



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

Connect to MySQL
conn = connect(
    "mysql",
    host="localhost",
    user="root",
    password="mypassword",
    database="testdb",
    port=3306  # optional, default is 3306
)

4.Connect to Azure SQL database.
