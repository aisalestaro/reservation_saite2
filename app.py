import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from datetime import datetime, timedelta, date
from db_config import User, Reservation, Inventory


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

def initialize_inventory(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        Inventory.create(date=current_date)
        current_date += timedelta(days=1)

def check_and_update_inventory(check_in_date, check_out_date):
    query = Inventory.select().where(Inventory.date.between(check_in_date, check_out_date - timedelta(days=1)))
    for inventory in query:
        if inventory.available_rooms > 0:
            inventory.available_rooms -= 1
            inventory.save()
        else:
            raise ValueError(f"No rooms available on {inventory.date}")

@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    if request.method == "POST":
        check_in_date = datetime.strptime(request.form["check_in_date"], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(request.form["check_out_date"], '%Y-%m-%d').date()
        try:
            check_and_update_inventory(check_in_date, check_out_date)
            # ...その他の予約処理
            # メール通知
            msg = Message("予約完了", recipients=[current_user.email])
            msg.body = f"予約が完了しました。チェックイン日: {check_in_date}, チェックアウト日: {check_out_date}"
            mail.send(msg)
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e))
    return render_template("reservation.html")

@app.route("/history")
@login_required
def history():
    reservations = Reservation.select().where(Reservation.user == current_user)
    return render_template("history.html", reservations=reservations)


@login_manager.user_loader
def load_user(user_id):
    return User.get(id=int(user_id))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST" and request.form["name"] and request.form['password'] and request.form["email"]:
        if User.select().where(User.name == request.form["name"]).first():
            flash("その名前はすでに使われています")
            return redirect(request.url)

        if User.select().where(User.email == request.form["email"]).first():
            flash("そのメールアドレスはすでに使われています")
            return redirect(request.url)

        try:
            user = User.create(
                name=request.form["name"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"]),
            )
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))
        except IntegrityError as e:
            flash(f"登録に失敗しました: {e}")
    return render_template("register.html")


# ログインフォームの表示・ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form["email"] and request.form["password"]:
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))
        else:
            flash("認証に失敗しました: Emailまたはパスワードが間違っています")
    return render_template("login.html")


# ログアウト処理
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました！")
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and current_user.is_authenticated:
        # 予約情報を取得
        room_type = request.form["room_type"]
        check_in_date = request.form["check_in_date"]
        check_out_date = request.form["check_out_date"]
        # その他の予約情報を取得...

        # 何泊かを計算
        number_of_stays = (datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.strptime(check_in_date, '%Y-%m-%d')).days

        # 新しい予約をデータベースに保存
        reservation = Reservation.create(
            user=current_user,
            room_type=room_type,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_stays=number_of_stays,
            # その他の予約情報...
        )

        # メール通知を送信
        send_reservation_email(reservation)

        flash("予約が完了しました!")
        return redirect(url_for("index"))

    # 予約履歴を取得
    reservations = (
        Reservation.select()
        .where(Reservation.user == current_user)
        .order_by(Reservation.check_in_date.desc())
    )
    return render_template("index.html", reservations=reservations)


def send_reservation_email(reservation):
    msg = Message("予約確認", recipients=[reservation.user.email])
    msg.body = f"予約内容:\n部屋タイプ: {reservation.room_type}\nチェックイン日: {reservation.check_in_date}\nチェックアウト日: {reservation.check_out_date}\n何泊: {reservation.number_of_stays}\n"  # ...その他の情報
    mail.send(msg)


@app.route("/reservations/<reservation_id>/delete/", methods=["POST"])
@login_required
def delete(reservation_id):
    if Reservation.select().where((Reservation.id == reservation_id) & (Reservation.user == current_user)).first():
        Reservation.delete_by_id(reservation_id)
    else:
        flash("無効な操作です")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

