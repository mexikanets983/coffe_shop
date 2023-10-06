import json
import requests
from geopy import distance
import folium
from flask import Flask
import os


def read_data(file_name="coffee.json"):
    with open(file_name, "r", encoding="CP1251") as my_file:
        file_content = my_file.read()
    data = json.loads(file_content)
    return data


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()
    if 'response' not in found_places:
        return None
    most_relevant = found_places['response']['GeoObjectCollection']['featureMember'][0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def calculate_distance(coffee_shops, user_coords):
    coffee_data = []
    for coffee_shop in coffee_shops:
        name = coffee_shop['Name']
        width = coffee_shop["Latitude_WGS84"]
        longitude = coffee_shop["Longitude_WGS84"]
        coords = (float(width), float(longitude))
        dist = distance.distance(coords, (float(user_coords[0]), float(user_coords[1]))).km
        coffee_info = {
            'name': name,
            'distance': dist,
            'latitude': width,
            'longitude': longitude
        }
        coffee_data.append(coffee_info)
    coffee_data_sorted = sorted(coffee_data, key=lambda k: k['distance'])
    return coffee_data_sorted[:5]


def create_map(coffee_shops, user_coords):
    m = folium.Map(location=[float(user_coords[0]), float(user_coords[1])], zoom_start=13)
    for coffee_info in coffee_shops:
        latitude = coffee_info['latitude']
        longitude = coffee_info['longitude']
        folium.Marker(
            location=[latitude, longitude],
            popup=coffee_info['name'],
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(m)
    m.save("index.html")


def serve_map():
    with open('index.html') as file:
        return file.read()


def main():
    data = read_data()
    apikey = os.environ['API_KEY']
    address = input("Где вы находитесь?:")
    coords_2 = fetch_coordinates(apikey, address)
    closest_coffee_shops = calculate_distance(data, coords_2)
    create_map(closest_coffee_shops, coords_2)
    app = Flask(__name__)
    app.add_url_rule('/', 'coffeemap', serve_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
