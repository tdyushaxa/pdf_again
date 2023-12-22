import sqlite3
import threading

db_lock = threading.Lock()
db_lock.acquire()
db_lock.release()


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        con = sqlite3.connect(self.path_to_db)
        return con

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
        except:
            cursor.close()

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
            CREATE TABLE Users (
                id int NOT NULL,
                Name varchar(255) NOT NULL,
                email varchar(255),
                language varchar(3),
                PRIMARY KEY (id)
                );
    """
        self.execute(sql, commit=True)

    def create_table_active_users(self):
        sql = """
            CREATE TABLE ActiveUsers (
                id int NOT NULL,
                Name varchar(255) NOT NULL,
                email varchar(255),
                language varchar(3),
                PRIMARY KEY (id)
                );
    """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, name: str, email: str = None, language: str = None):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
            INSERT INTO Users(id, Name, email, language) VALUES(?, ?, ?, ?)
            """
        self.execute(sql, parameters=(id, name, email, language), commit=True)

    def add_active_user(self, id: int, name: str, email: str = None, language: str = 'uz'):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
            INSERT INTO ActiveUsers(id, Name, email, language) VALUES(?, ?, ?, ?)
            """
        self.execute(sql, parameters=(id, name, email, language), commit=True)

    def select_all_users(self):
        sql = """
            SELECT * FROM Users
            """
        return self.execute(sql, fetchall=True)

    def select_all_active_users(self):
        sql = """
            SELECT * FROM ActiveUsers
            """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def select_active_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM ActiveUsers WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def count_active_users(self):
        return self.execute("SELECT COUNT(*) FROM ActiveUsers;", fetchone=True)

    def update_user_email(self, email, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
            UPDATE Users SET email=? WHERE id=?
            """
        return self.execute(sql, parameters=(email, id), commit=True)

    def update_user_langugae(self, language, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
            UPDATE Users SET language=? WHERE id=?
            """
        return self.execute(sql, parameters=(language, id), commit=True)

    def delete_user(self, id):
        sql_update_query = "DELETE FROM ActiveUsers WHERE id=?"
        self.execute(sql_update_query, (id,), commit=True)

    def delete_active_user(self, id):
        sql_update_query = "DELETE FROM ActiveUsers WHERE id=?"
        self.execute(sql_update_query, (id,), commit=True)


def logger(statement):
    print(f"""
    _____________________________________________________        
    Executing: 
    {statement}
    _____________________________________________________
    """)
