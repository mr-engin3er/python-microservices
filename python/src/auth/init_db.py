import os
import psycopg2

HOST=os.getenv('HOST',"192.168.1.42")
DATABASE=os.getenv('DATABASE',"auth")
USER=os.getenv('POSTGRES_USER','root')
PASSWORD=os.getenv('POSTGRES_PASSWORD','root')

conn = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD)

try:
        conn.autocommit = True
        with conn.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE "{DATABASE}";')
except OSError as e:
        print("error",e)
finally:
        conn.close()

conn = psycopg2.connect(
        host=HOST,
        user=USER,
        database=DATABASE,
        password=PASSWORD)
# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
# cur.execute(f"CREATE USER auth_user WITH ENCRYPTED PASSWORD 'Auth@123';")
cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('CREATE TABLE users (id  SERIAL PRIMARY KEY,'
                                 'email VARCHAR(150) NOT NULL UNIQUE,'
                                 'password VARCHAR(255) NOT NULL,'
                                 'created_at date DEFAULT CURRENT_TIMESTAMP);'
                                 )

# Insert data into the table

cur.execute('INSERT INTO users (email, password)'
            'VALUES (%s, %s)',
            ('dheeraj@gmail.com',
             'Admin@123',)
            )


conn.commit()

cur.close()
conn.close()