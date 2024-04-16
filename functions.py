from amadeus import ResponseError, Client
import requests
from config import API_AMADEUS, SECRET_KEY_AMADEUS, API_YANDEX_SCHEDULE, API_YANDEX_GEOCODER
import json
import datetime as dt
from random import choice


def get_hotels_by_city(city):
    amadeus = Client(
        client_id=API_AMADEUS,
        client_secret=SECRET_KEY_AMADEUS
    )
    try:
        '''
        Get list of hotels by city code
        '''
        city_code = \
            requests.get(f'https://www.travelpayouts.com/widgets_suggest_params?q=Из%20{city}%20в%20Лондон').json()[
                'origin']['iata']
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)

        return response.data[:5]
    except ResponseError as error:
        raise error


def get_transport(fr, to, date):
    response = requests.get(
        f"https://api.rasp.yandex.net/v3.0/search/?apikey={API_YANDEX_SCHEDULE}&format=json&from={fr}&to={to}&lang=ru_RU&page=1&date={date}&system=iata&transfers=true&limit=10").json()
    if response.get("error", None) is None:
        with open("static/json/transport.json", "r") as file:
            json_data = json.load(file)

        if fr not in json_data["transport_schedule"]["cities_iata"]:
            json_data["transport_schedule"]["cities_iata"][fr] = {}
        if to not in json_data["transport_schedule"]["cities_iata"][fr]:
            json_data["transport_schedule"]["cities_iata"][fr][to] = {}
        if date not in json_data["transport_schedule"]["cities_iata"][fr][to]:
            data_to_json = {}

            for index, toponym in enumerate(response['segments']):
                block = []
                if toponym["has_transfers"]:
                    for transfer in toponym["details"]:
                        thread = {}
                        if transfer.get("is_transfer", None) is None:
                            thread["name"] = transfer["thread"]["title"]
                            thread["fr"] = transfer["from"]["title"]
                            thread["to"] = transfer["to"]["title"]
                            thread["transport"] = transfer["thread"]["transport_type"]
                            thread["start"] = dt.datetime.strptime(transfer["departure"][:16],
                                                                   "%Y-%m-%dT%H:%M").strftime('%H:%M %d.%m.%Y')
                            thread["end"] = dt.datetime.strptime(transfer["arrival"][:16],
                                                                 "%Y-%m-%dT%H:%M").strftime(
                                '%H:%M %d.%m.%Y')
                            block.append(thread)
                else:
                    thread = {'id': index}
                    thread["name"] = toponym["thread"]["title"]
                    thread["fr"] = toponym["from"]["title"]
                    thread["to"] = toponym["to"]["title"]
                    thread["transport"] = toponym["thread"]["transport_type"]
                    start = toponym["departure"].split('T')
                    thread["start"] = dt.datetime.strptime(toponym["departure"][:16], "%Y-%m-%dT%H:%M").strftime(
                        '%H:%M %d.%m.%Y')
                    thread["end"] = dt.datetime.strptime(toponym["arrival"][:16], "%Y-%m-%dT%H:%M").strftime(
                        '%H:%M %d.%m.%Y')
                    block.append(thread)
                data_to_json[index + 1] = block
            json_data["transport_schedule"]["cities_iata"][fr][to][date] = data_to_json
            with open("static/json/transport.json", "w", encoding="utf-8") as out_file:
                json.dump(json_data, out_file)
        else:
            data_to_json = json_data["transport_schedule"]["cities_iata"][fr][to][date]
        return data_to_json
    return None


def get_placemark(city):
    from_coords = requests.get(
        f"https://geocode-maps.yandex.ru/1.x/?apikey={API_YANDEX_GEOCODER}&geocode={city}&format=json").json()
    if from_coords:
        fr = from_coords['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        center_points = [float(x) for x in fr.split()[::-1]]
        city_iata = ''
        with open('static/json/iata_codes.json', 'r', encoding='utf-8') as f:
            codes = json.load(f)
        if city.capitalize() in codes['city_to_iata']:
            city_iata = codes['city_to_iata'][city.capitalize()]
        else:
            iata_codes = requests.get(
                f"https://www.travelpayouts.com/widgets_suggest_params?q=https://www.travelpayouts.com/widgets_suggest_params?q=%20{city}%20Лондон").json()
            if iata_codes:
                city_iata = iata_codes['origin']['iata']
                codes['city_to_iata'][city.capitalize()] = city_iata
                codes['iata_to_city'][city_iata] = city.capitalize()
                with open('static/json/iata_codes.json', 'w', encoding='utf-8') as out:
                    json.dump(codes, out)
            return None
        if city_iata:
            index_route = get_route_index(city_iata)
            coords_data = {'center_points': center_points, 'city': city, 'city_iata': city_iata, 'index': index_route}
            return coords_data
        return None
    return None


def add_to_json(route):
    with open("static/json/route.json", "r") as file:
        json_data = json.load(file)
    if route["city_iata"] not in json_data["routes"]["cities"]:
        json_data["routes"]["cities"][route["city_iata"]] = {}
    index = get_route_index(route["city_iata"])
    if route.get('route', None) is not None:
        data_to_json = []
        for coords in route["route"]:
            lat, lon = coords
            data_to_json.append((lat, lon))
        json_data["routes"]["cities"][route["city_iata"]][index] = data_to_json
        with open("static/json/route.json", "w", encoding="utf-8") as out_file:
            json.dump(json_data, out_file)
        return index

    data_to_json = route['points']
    json_data["routes"]["cities"][route["city_iata"]][index] = data_to_json
    with open("static/json/route.json", "w", encoding="utf-8") as out_file:
        json.dump(json_data, out_file)
    return index


def get_route_index(city_iata):
    with open("static/json/route.json", "r") as file:
        json_data = json.load(file)

    if city_iata not in json_data["routes"]["cities"] or not json_data["routes"]["cities"][city_iata]:
        return "1"
    return str(int(list(json_data["routes"]["cities"][city_iata].keys())[-1]) + 1)


def create_routes(from_coords, to_coords, city_iata):
    url = 'https://sightsafari.city/api/v1/routes/direct'
    params = {
        'from': ','.join(map(str, from_coords)),
        'to': ','.join(map(str, to_coords)),
        'ratio': 0.5,
        'locale': 'ru'
    }
    response = requests.get(url, params=params).json()
    if response.get('code', 404) == 0:
        index = add_to_json({'city_iata': city_iata, 'points': response['body']['latLonPoints']})
    return index



