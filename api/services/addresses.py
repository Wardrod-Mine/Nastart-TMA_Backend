import json
import re

import aiohttp
from shapely.geometry import Point, Polygon


async def calculate_delivery_price(address: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://geocode-maps.yandex.ru/1.x/?apikey=da828657-8539-4316-bc0a-7edd7dccf4f3&geocode={address}&format=json"
        ) as response:
            data = await response.json()
            ll = data["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"
            ]["Point"]["pos"].split(" ")
            point = Point(list(map(float, ll)))
    with open("delivery.geojson") as f:
        zones = json.load(f)["features"]
        for zone in zones:
            if zone["geometry"]["type"] != "Polygon":
                continue
            polygon = Polygon(zone["geometry"]["coordinates"][0])
            if polygon.contains(point):
                # get price from zone['properties']['description'] like asdjgfa 123 ₽ wgawgew
                pattern = r"(\d+)\s*₽"
                match = re.search(pattern, zone["properties"]["description"])
                if match:
                    return int(match.group(1))
                else:
                    return 0
    return None
