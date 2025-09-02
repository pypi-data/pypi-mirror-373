from peewee import MySQLDatabase


class DatabaseConnection:
    def __init__(self, db_name, user, password, host):
        self.db = MySQLDatabase(db_name, user=user, password=password, host=host)

    def connect(self):
        self.db.connect()

    def close(self):
        if not self.db.is_closed():
            self.db.close()

    def get_db(self):
        return self.db
