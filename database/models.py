from peewee import *
from loader import db


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField(unique=True)
    name = CharField(unique=True)

    class Meta:
        db_table = 'users'
        order_by = 'id'


class History(BaseModel):
    date = DateField()
    command = CharField()
    city = CharField()
    start_date = DateField()
    end_date = DateField()
    from_user = ForeignKeyField(User.name)

    class Meta:
        db_table = 'histories'
        order_by = 'date'


class SearchResult(BaseModel):
    hotel_id = IntegerField()
    hotel_name = CharField()
    price_per_night = FloatField()
    total_price = FloatField()
    distance_city_center = FloatField()
    hotel_url = CharField()
    hotel_neighbourhood = CharField()
    from_date = ForeignKeyField(History.date)

    class Meta:
        db_table = 'results'
        order_by = 'price_per_night'
