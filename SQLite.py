#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

class SQLite:

    def __init__(self):
        self.connection = sqlite3.connect('core.db')
        self.cursor = self.connection.cursor()

    def use_your_power(self, sql, data=None):
        if data==None:
            try:
                with self.connection:
                    a = self.connection.execute(sql)
                    self.connection.commit()
                    return a
            except sqlite3.Error as e:
                print(e)
                return e
        else:
            try:
                with self.connection:
                    a = self.connection.execute(sql, data)
                    self.connection.commit()
                    return a
            except sqlite3.Error as e:
                print(e)
                return e
