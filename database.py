import mysql.connector

class Database:

    def __init__(self):

        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="",
            database="py_gym",
            use_pure=True
        )

        self.cursor = self.conn.cursor()

        print("Database Connected")