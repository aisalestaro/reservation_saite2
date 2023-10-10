import os
import datetime
import logging
from playhouse.db_url import connect
from dotenv import load_dotenv
from peewee import Model, IntegerField, CharField, TextField, DateField, TimestampField

# .envの読み込み
load_dotenv()

# ①実行したSQLをログで出力する設定
logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# ②データベースへの接続設定
# db = SqliteDatabase("peewee_db.sqlite")  # SQLite固定の場合
db = connect(os.environ.get("DATABASE"))  # 環境変数に合わせて変更する場合
# db = connect(os.environ.get("DATABASE") or "sqlite:///peewee_db.sqlite")  # 環境変数が無い場合にデフォルト値として値を設定することも可能

# 接続NGの場合はメッセージを表示
if not db.connect():
    print("接続NG")
    exit()


# ③メッセージのモデル
class Reservation(Model):
    id = IntegerField(primary_key=True)
    guest_name = CharField()  # 宿泊者氏名
    address = TextField()  # 住所
    email = CharField()  # メールアドレス
    male_guests = IntegerField()  # 男性の数
    female_guests = IntegerField()  # 女性の数
    phone_number = CharField()  # 宿泊者電話番号
    reservation_date = DateField()  # 宿泊日
    number_of_stays = IntegerField()  # 宿泊数
    check_in_time = CharField()  # チェックイン時刻
    remarks = TextField()
    pub_date = TimestampField(default=datetime.datetime.now)  # 何も指定しない場合は現在時刻が入る

    class Meta:
        database = db
        table_name = "reservations"  # テーブル名を修正


db.create_tables([Reservation])  # テーブル作成の修正
