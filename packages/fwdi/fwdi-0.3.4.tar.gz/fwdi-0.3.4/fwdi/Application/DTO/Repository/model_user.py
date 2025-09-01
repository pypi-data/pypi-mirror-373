from .model_permission import *


class User(DbContextFWDI):
    id = PrimaryKeyField()
    username = CharField()
    full_name = CharField()
    email = CharField()
    hashed_password = CharField()
    disabled = BooleanField()
    scopes = ForeignKeyField(Permissions)
