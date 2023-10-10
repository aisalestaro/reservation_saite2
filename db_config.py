import os
import datetime
import logging
from playhouse.db_url import connect
from dotenv import load_dotenv
from peewee import Model, IntegerField, CharField, TextField, TimestampField
from peewee import *
import datetime

database = SqliteDatabase('reservation.db')

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    join_date = DateTimeField(default=datetime.datetime.now)
    
    @property
    def is_active(self):
        # この例ではすべてのユーザーをアクティブとして扱います。
        # 必要に応じて、ユーザーがアクティブかどうかをチェックするロジックを追加できます。
        return True
    
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True  # Or your appropriate logic here
class Reservation(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref='reservations')
    guest_name = CharField()
    address = TextField()
    email = CharField()
    male_guests = IntegerField()
    female_guests = IntegerField()
    phone_number = CharField()
    room_type = CharField(default='Double Room')  
    check_in_date = DateField()
    check_out_date = DateField()
    number_of_stays = IntegerField()
    check_in_time = CharField()
    remarks = TextField()
    pub_date = DateTimeField()

class Inventory(BaseModel):
    date = DateField(unique=True)
    available_rooms = IntegerField(default=10) 

if __name__ == '__main__':
    database.connect()
    database.create_tables([User, Reservation, Inventory])