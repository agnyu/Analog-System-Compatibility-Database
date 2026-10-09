import mysql.connector
import os
import re
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )

def fetch_all(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def fetch_one(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def execute_query(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def execute_many(query, values):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.executemany(query, values)
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def get_lookup_table(table_name, id_col, name_col):
    if not re.match(r'^[a-zA-Z0-9_]+$', str(table_name)):
        raise ValueError("Invalid input")
    if not re.match(r'^[a-zA-Z0-9_]+$', str(id_col)):
        raise ValueError("Invalid input")
    if not re.match(r'^[a-zA-Z0-9_]+$', str(name_col)):
        raise ValueError("Invalid input")
    query = f"SELECT {id_col}, {name_col} FROM {table_name} ORDER BY {name_col};"
    return fetch_all(query)