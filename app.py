# db.config.pyからデータをインポートします
from db_config import Reservation, db

def select_action():
    # ユーザーにアクションを選択させる
    return input("番号を入力してください\n1:新しい予約 2:予約表示 3:予約キャンセル 0:終了>")

def add_reservation():
    # 新しい予約を追加する
    guest_name = input("宿泊者氏名を入力してください>")
    address = input("住所を入力してください>")
    email = input("メールアドレスを入力してください>")
    male_guests = int(input("男性の数を入力してください>"))
    female_guests = int(input("女性の数を入力してください>"))
    phone_number = input("電話番号を入力してください>")
    reservation_date = input("宿泊日をYYYY-MM-DD形式で入力してください>")
    number_of_stays = int(input("宿泊数を入力してください>"))
    check_in_time = input("チェックイン時刻を入力してください>")
    remarks = input("備考を入力してください>")

    # データベースに新しい予約を保存する
    Reservation.create(
        guest_name=guest_name,
        address=address,
        email=email,
        male_guests=male_guests,
        female_guests=female_guests,
        phone_number=phone_number,
        reservation_date=reservation_date,
        number_of_stays=number_of_stays,
        check_in_time=check_in_time,
        remarks=remarks
    )
    print("予約の登録1に成功しました")

def show_reservations():
    # すべての予約を表示する
    for reservation in Reservation.select():
        print(f"予約ID: {reservation.id}, 宿泊者氏名: {reservation.guest_name}, 宿泊日: {reservation.reservation_date}")

def cancel_reservation():
    # 予約をキャンセルする
    reservation_id = int(input("キャンセルする予約のIDを入力してください>"))
    reservation = Reservation.get_or_none(Reservation.id == reservation_id)
    if reservation is not None:
        reservation.delete_instance()
        print("予約のキャンセルに成功しました")
    else:
        print("指定された予約IDは存在しないため、キャンセルできませんでした")

def main():
    while True:
        action = select_action()

        if action == "1":
            add_reservation()
            continue

        if action == "2":
            show_reservations()
            continue

        if action == "3":
            cancel_reservation()
            continue

        if action == "0":
            print("終了します")
            break

        print("入力に誤りがありますので、もう一度最初からやり直してください")

if __name__ == "__main__":
    main()
