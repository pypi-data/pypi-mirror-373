from ....Application.Abstractions.db_context import *

class Scope(DbContextFWDI):
    id = PrimaryKeyField()
    name = CharField()
    description = CharField()