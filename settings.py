import sqlite3


class Settings:


    def __init__(self, token=None, donation=None):
        self.token = token
        self.donation = donation


    @classmethod
    def open(self):
        base = sqlite3.connect('base.db')
        cursor = base.cursor()
        settings = cursor.execute('select * from Settings').fetchall()[0]
        base.close()
        return Settings(settings[0], settings[1])
