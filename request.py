import requests
import asyncio


async def post_request_for_road_deficiencie(road_name, x, y) -> bool:
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/unverified'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.post(url, json=location)
    status = response.status_code == requests.codes.ok
    return status


async def post_request_for_photo(road_name, img) -> bool:
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/unverified'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.post(url, json=location)
    status = response.status_code == requests.codes.ok
    return status


async def get_request_for_map(road_name, x, y):
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/gasStations'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.get(url, params=location)
    return response.json()
