
import os
from flask_login import current_user
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from db_config import User, Reservation
from flask_mail import Mail, Message  # メール通知のため

app = Flask(__name__)  # appオブジェクトを作成
app.secret_key = os.urandom(24)

mail = Mail(app)  # ここにMailオブジェクトの初期化を移動

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    if request.method == "POST":
        check_in_date = request.form["check_in_date"]
        check_out_date = request.form["check_out_date"]
        # ... 在庫確認と予約処理
        # メール通知
        msg = Message("予約完了", recipients=[current_user.email])
        msg.body = f"予約が完了しました。チェックイン日: {check_in_date}, チェックアウト日: {check_out_date}"
        mail.send(msg)
        return redirect(url_for("index"))
    return render_template("reservation.html")

@app.route("/history")
@login_required
def history():
    reservations = Reservation.select().where(Reservation.user == current_user)
    return render_template("history.html", reservations=reservations)


app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

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
        except IntegrityError:
            flash("登録に失敗しました")
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
            flash("認証に失敗しました")
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
        Reservation.create(user=current_user, content=request.form["content"])  
    messages = (
        Reservation.select()
        .order_by(Reservation.pub_date.desc(), Reservation.id.desc())
    )
    return render_template("index.html", messages=messages)

@app.route("/reservations/<reservation_id>/delete/", methods=["POST"])
@login_required
def delete(reservation_id):
    if Reservation.select().where((Reservation.id == reservation_id) & (Reservation.user == current_user.id)).first():
        Reservation.delete_by_id(reservation_id)
    else:
        flash("無効な操作です")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
