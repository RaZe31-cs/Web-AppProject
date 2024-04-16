import sys
import requests
import datetime as dt
import json
from flask import Flask
from flask import render_template, redirect, request, abort, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.trips import Trip
from forms.user import RegisterForm, LoginForm
from forms.trip import TripForm
# from forms.hotel import HotelForm
from functions import get_hotels_by_city, get_transport, get_placemark, add_to_json, create_routes

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

CURRENT_TRIP = {}


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


@app.route("/profile")
def profile():
    db_sess = db_session.create_session()
    trips = []
    trips_db = db_sess.query(Trip).filter(Trip.user_id == current_user.id).all()
    with open('static/json/iata_codes.json', 'r', encoding='utf-8') as f:
        codes = json.load(f)
    with open('static/json/transport.json', 'r', encoding='utf-8') as f:
        transport = json.load(f)
    with open('static/json/route.json', 'r', encoding='utf-8') as f:
        routes_json = json.load(f)
    for t in trips_db:
        block = {}
        block['city_from'] = codes['iata_to_city'][t.city_from]
        block['city_to'] = codes['iata_to_city'][t.city_to]
        block['date'] = t.date.strftime('%Y-%m-%d')
        block['transport'] = transport['transport_schedule']['cities_iata'][t.city_from][t.city_to][block['date']][
            str(t.transport_id)]
        block['routes'] = []
        if t.list_of_routes is not None and t.list_of_routes:
            for route in t.list_of_routes.split(','):
                points = routes_json['routes']['cities'][t.city_to][route]
                block['routes'].append(get_image(points, t.city_to, route))
            print(block)
        trips.append(block)
    return render_template('profile.html', trips=trips)


def get_image(pt, city, index, l='map', delta=0.005):
    org_point = ["{1},{0}".format(*point) for point in pt]
    pt_str = "{0},vkbkm~{1},vkbkm".format(org_point[0], org_point[-1])

    pl_str = "c:463830FF," + ','.join(org_point)

    map_params = {
        "l": l,
        "pt": pt_str,
        "pl": pl_str,
        "size": '300,200'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    if not response:
        sys.exit()

    map_file = f"static/img/{city}{index}.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return map_file


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/save_trip')
def create_trip():
    if CURRENT_TRIP:
        print(CURRENT_TRIP)
        db_sess = db_session.create_session()
        trip = Trip(
            city_from=CURRENT_TRIP['city_from'],
            city_to=CURRENT_TRIP['city_to'],
            date=CURRENT_TRIP['date'],
            transport_id=CURRENT_TRIP['transport_id'],
            hotel_id=CURRENT_TRIP['hotel_id'],
            list_of_routes=','.join(map(str, CURRENT_TRIP['list_of_routes']))
        )
        current_user.trips.append(trip)
        db_sess.merge(current_user)
        db_sess.commit()
    return redirect("/")


@app.route("/start", methods=['GET', 'POST'])
def start_trip():
    global CURRENT_TRIP
    form = TripForm()
    if request.args:
        args = request.args
        fr, to, transport_id = args.get('from'), args.get('to'), args.get('id')
        date = dt.datetime.strptime(args.get('date'), '%Y-%m-%d')
        CURRENT_TRIP = {'city_from': fr,
                        'city_to': to,
                        'date': date,
                        'transport_id': transport_id,
                        'hotel_id': 1,
                        'list_of_routes': []}
        with open('static/json/iata_codes.json', 'r', encoding='utf-8') as f:
            codes = json.load(f)
            city = codes['iata_to_city'][to]
        return redirect(url_for('choose_hotel', city=city))
    else:
        if form.validate_on_submit():
            if 'submit_next' in request.form:
                print('Далее')
            else:
                from_text = form.from_text.data
                to_text = form.to_text.data
                date = form.date.data

                iata_codes = requests.get(
                    f"https://www.travelpayouts.com/widgets_suggest_params?q=https://www.travelpayouts.com/widgets_suggest_params?q=%20{from_text}%20{to_text}").json()
                if iata_codes:
                    fr, to = iata_codes['origin']['iata'], iata_codes['destination']['iata']
                    with open('static/json/iata_codes.json', 'r', encoding='utf-8') as f:
                        codes = json.load(f)
                        codes['city_to_iata'][from_text.capitalize()], codes['city_to_iata'][
                            to_text.capitalize()] = fr, to
                        codes['iata_to_city'][fr], codes['iata_to_city'][
                            to] = from_text.capitalize(), to_text.capitalize()
                    with open('static/json/iata_codes.json', 'w', encoding='utf-8') as out:
                        json.dump(codes, out)
                    date = date.strftime('%Y-%m-%d')
                    data = get_transport(fr, to, date)
                    if data is not None:
                        data = list(data.values())
                        return render_template('transport.html', form=form, data=data, fr=fr, to=to, date=date)
                    return render_template('transport.html', form=form, message="Данные некорректны")
                return render_template('transport.html', form=form, message="Данные некорректны")
        return render_template('transport.html', form=form)


@app.route('/route/<city>', methods=['GET', 'POST'])
def routes(city):
    if request.method == 'POST':
        data = request.json
        if data['type'] == 'new' and data['route']:
            index = add_to_json(data)
        else:
            index = data['index']
        if index not in CURRENT_TRIP['list_of_routes']:
            CURRENT_TRIP['list_of_routes'].append(index)
    coords_data = get_placemark(city)
    return render_template('route.html', data=coords_data)


@app.route('/route/generate', methods=['POST'])
def generate_routes():
    data = request.json
    index = create_routes(data['start'], data['end'], data['city_iata'])
    with open('static/json/route.json', 'r') as f:
        coords = json.load(f)['routes']['cities'][data['city_iata']][index]
    return {'coords': coords, 'index': index}


@app.route("/start/choose_hotel/<city>", methods=['GET', 'POST'])
def choose_hotel(city):
    hotels = get_hotels_by_city(city)
    print(hotels)
    return render_template("index.html", hotels=hotels)


def main():
    db_session.global_init("db/web_project.db")
    app.run(debug=True)


if __name__ == '__main__':
    main()
