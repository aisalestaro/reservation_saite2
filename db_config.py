# db_config.py
import os
import datetime
import logging
from dotenv import load_dotenv
from playhouse.db_url import connect
from peewee import Model, IntegerField, CharField, TextField, TimestampField, ForeignKeyField, DateField
from flask_login import UserMixin

load_dotenv()

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = connect(os.environ.get("DATABASE", "sqlite:///db.sqlite"))

if not db.connect():
    print("接続NG")
    exit()

class User(UserMixin, Model):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True)
    email = CharField(unique=True)
    password = TextField()
    join_date = TimestampField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_name = "users"

class Reservation(Model):
    id = IntegerField(primary_key=True)
    user = ForeignKeyField(User, backref='reservations')  # ユーザーとの関連を示す
    guest_name = CharField()  # 宿泊者氏名
    address = TextField()  # 住所
    email = CharField()  # メールアドレス
    male_guests = IntegerField()  # 男性の数
    female_guests = IntegerField()  # 女性の数
    phone_number = CharField()  # 宿泊者電話番号
    room_type = CharField(default="ダブルルーム")  # 客室タイプ
    check_in_date = DateField()  # チェックイン日
    check_out_date = DateField()  # チェックアウト日
    number_of_stays = IntegerField()  # 宿泊数
    check_in_time = CharField()  # チェックイン時刻
    remarks = TextField()  # 備考
    pub_date = TimestampField(default=datetime.datetime.now)  # 予約作成日時

    class Meta:
        database = db
        table_name = "reservations"


db.create_tables([User, Reservation])  # 変更

