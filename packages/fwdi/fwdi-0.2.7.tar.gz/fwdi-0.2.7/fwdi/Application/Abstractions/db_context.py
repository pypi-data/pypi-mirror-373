from peewee import *

db = SqliteDatabase('db.sqlite3')

class DbContextFWDI(Model):
    class Meta:
        database = db