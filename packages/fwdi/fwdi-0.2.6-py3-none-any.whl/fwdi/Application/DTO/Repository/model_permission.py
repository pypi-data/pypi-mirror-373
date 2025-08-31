from .model_scope import *

class Permissions(DbContextFWDI):
    id = PrimaryKeyField()
    name = CharField()
    scopes_detail = ManyToManyField(Scope, backref='scopes')