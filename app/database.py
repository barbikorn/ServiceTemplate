from typing import Optional
from psycopg2 import connect, extensions
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class Database:
    def __init__(self, db_name: str, username: str, password: str, host: str, port: str):
        self.conn = connect(
            dbname=db_name,
            user=username,
            password=password,
            host=host,
            port=port
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_database(db_name: str, host: str, port: int, username: str, password: str) -> Optional[MongoClient]:
    try:
        client = MongoClient(host=host, port=port, username=username, password=password)
        return client[db_name]
    except:
        print("Unable to connect to database")
        return None


def get_database_atlas(db_name: str,uri : str) -> Optional[MongoClient]:
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        return client[db_name]
    except:
        print("Unable to connect to database")
        return None

def get_database_pg(db_type: str, db_name: str, host: str, port: str, username: str, password: str) -> Optional[Database]:
    if db_type == 'postgresql':
        try:
            conn = Database(
                db_name=db_name,
                username=username,
                password=password,
                host=host,
                port=port
            )
            return conn
        except:
            print("Unable to connect to database")
            return None
    else:
        print("Invalid database type")
        return None

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")