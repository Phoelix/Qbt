import sqlite3

class SQLite:

    def __init__(self):
        self.connection = sqlite3.connect('core.db')
        self.cursor = self.connection.cursor()

    def add_member(self, data):
        sql = 'INSERT INTO members (tgID, uname, fname) VALUES (?,?,?)'
        try:
            with self.connection:
                self.connection.execute(sql, data)
                self.connection.commit()
        except sqlite3.Error as e:
            return e

    def get_member(self, data):
        sql = 'SELECT 1 FROM members WHERE tgID = ?'
        try:
            with self.connection:
                self.connection.execute(sql, data)
                self.connection.commit()
        except sqlite3.Error as e:
            return e

    def add_transct(self, data):
        sql = 'INSERT INTO transactions (ID, tgID, RUB, BTC, wallet, tcheck, status) VALUES (?,?,?,?,?,?,?)'
        try:
            with self.connection:
                self.connection.execute(sql, data)
                self.connection.commit()
        except sqlite3.Error as e:
            return e