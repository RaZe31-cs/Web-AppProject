from amadeus import ResponseError, Client
import requests
from config import API_AMADEUS, SECRET_KEY_AMADEUS


def get_hotels_by_city(city):
    amadeus = Client(
        client_id=API_AMADEUS,
        client_secret=SECRET_KEY_AMADEUS
    )
    try:
        '''
        Get list of hotels by city code
        '''
        city_code = requests.get(f'https://www.travelpayouts.com/widgets_suggest_params?q=Из%20{city}%20в%20Лондон').json()['origin']['iata']
        response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)

        return response.data[:5]
    except ResponseError as error:
        raise error
