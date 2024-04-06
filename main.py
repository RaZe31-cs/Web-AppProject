import requests
import datetime as dt
from flask import Flask
from flask import render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.trip import TripForm
from forms.hotel import HotelForm
from functions import get_hotels_by_city

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

api_key_yandex_schedule = '35dacd21-6ae5-4441-8c4b-ed23913a97b5'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form, message="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/start", methods=['GET', 'POST'])
def start_trip():
    form = TripForm()
    data = []
    print(request.form)
    if form.validate_on_submit():
        print(request.form)
        if 'submit_next' in request.form:
            print('Далее')
        else:
            from_text = form.from_text.data
            to_text = form.to_text.data
            date = form.date.data
            iata_codes = requests.get(f"https://www.travelpayouts.com/widgets_suggest_params?q=https://www.travelpayouts.com/widgets_suggest_params?q=%20{from_text}%20{to_text}").json()
            if iata_codes:
                fr, to = iata_codes['origin']['iata'], iata_codes['destination']['iata']
                response = requests.get(f"https://api.rasp.yandex.net/v3.0/search/?apikey={api_key_yandex_schedule}&format=json&from={fr}&to={to}&lang=ru_RU&page=1&date={date}&system=iata&transfers=true&limit=10").json()
                # print(str(response).replace("'", '"'))
                if response.get("error", None) is None:
                    for toponym in response['segments']:
                        block = []
                        if toponym["has_transfers"]:
                            for transfer in toponym["details"]:
                                thread = {}
                                if transfer.get("is_transfer", None) is None:
                                    thread["name"] = transfer["thread"]["title"]
                                    thread["fr"] = transfer["from"]["title"]
                                    thread["to"] = transfer["to"]["title"]
                                    thread["transport"] = transfer["thread"]["transport_type"]
                                    thread["start"] = dt.datetime.strptime(transfer["departure"][:16], "%Y-%m-%dT%H:%M").strftime('%H:%M %d.%m.%Y')
                                    thread["end"] = dt.datetime.strptime(transfer["arrival"][:16], "%Y-%m-%dT%H:%M").strftime('%H:%M %d.%m.%Y')
                                    block.append(thread)
                        else:
                            thread = {}
                            thread["name"] = toponym["thread"]["title"]
                            thread["fr"] = toponym["from"]["title"]
                            thread["to"] = toponym["to"]["title"]
                            thread["transport"] = toponym["thread"]["transport_type"]
                            start = toponym["departure"].split('T')
                            thread["start"] = dt.datetime.strptime(toponym["departure"][:16], "%Y-%m-%dT%H:%M").strftime('%H:%M %d.%m.%Y')
                            thread["end"] = dt.datetime.strptime(toponym["arrival"][:16], "%Y-%m-%dT%H:%M").strftime('%H:%M %d.%m.%Y')
                            block.append(thread)
                        data.append(block)
                    # print(data)
                    return render_template('transport.html', form=form, data=data)
                return render_template('transport.html', form=form, message="Данные некорректны")
            return render_template('transport.html', form=form, message="Данные некорректны")
    return render_template('transport.html', form=form)
'''    if request.method == 'GET':
        return render_template("transport.html")
    else:
        
        print(from_text, to_text, date)
        if not from_text or not to_text or not date:
             print('Please enter all the fields.')
        else:
            response = requests.get(
                f"https://api.rasp.yandex.net/v3.0/search/?apikey={api_key_yandex_schedule}&format=json&from=c146&to=c213&lang=ru_RU&page=1&date=2024-09-02")
            print(response.json())'''


@app.route("/start/choose_hotel/<city>", methods=['GET', 'POST'])
def choose_hotel(city):
    hotels = get_hotels_by_city(city)
    print(hotels)
    return render_template("choose_hotel.html", hotels=hotels)


def main():
    db_session.global_init("db/web_project.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
