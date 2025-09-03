
    
    
    # db/conn.py
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import sqlite3


def mysql(user: str, password: str, host: str, port: int, database: str = None):
    """
    Connect to a MySQL database using SQLAlchemy.
    Returns (engine, connection).
    """
    try:
        conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}"
        if database:
            conn_str += f"/{database}"

        engine = create_engine(conn_str)
        conn = engine.connect()

        print("✅ MySQL connection established.")
        return engine, conn
    except Exception as e:
        print("❌ MySQL connection failed:", e)
        return None, None


def mysql_execute(conn, query: str):
    """
    Execute a query on MySQL safely using SQLAlchemy 2.x.
    Returns the result object (or None on error).
    """
    try:
        result = conn.execute(text(query))
        return result
    except Exception as e:
        print("❌ MySQL query failed:", e)
        return None


def mongodb(uri: str, db_name: str):
    """
    Connect to a MongoDB database using pymongo.
    Returns (client, db).
    """
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print("✅ MongoDB connection established.")
        return client, db
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        return None, None


def sqlite(db_path: str):
    """
    Connect to a SQLite database.
    Returns (conn, cursor).
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ SQLite connection established.")
        return conn, cursor
    except Exception as e:
        print("❌ SQLite connection failed:", e)
        return None, None
