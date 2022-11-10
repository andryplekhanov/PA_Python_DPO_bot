from peewee import *
from loader import db


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel):
    name = CharField()

    class Meta:
        db_table = 'users'


class History(BaseModel):
    date = DateField()
    command = CharField()
    hotels = CharField()
    user_id = ForeignKeyField(User)

    class Meta:
        db_table = 'histories'
