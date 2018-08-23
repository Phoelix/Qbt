import sqlite3

class SQLite:

    def __init__(self):
        self.connection = sqlite3.connect('core.db')
        self.cursor = self.connection.cursor()

    def use_your_power(self, sql, data=None):
        try:
            with self.connection:
                self.connection.execute(sql, data)
                self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            return e