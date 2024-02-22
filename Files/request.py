import requests


async def get_request_urgent_message(road_name):
    url = f'http://backend/api/roads/{road_name}/'
    road = {'roadName': ''}
    response = requests.get(url, params=road)
    return response.json()


async def post_request_location_and_description(
        road_name: str,
        longitude: float,
        latitude: float,
        type_road: str,
        description: str = None
):
    url = f'http://backend/api/roads/{road_name}/unverified'
    data = {
        'point': {
            'description': description,
            'type': type_road,
            'coordinates': {
                'longitude': longitude,
                'latitude': latitude,
            }
        },
        'roadName': road_name
    }
    response = requests.post(url, json=data)
    return response.json()


async def post_request_media(file_id, point_id, type_media):
    url = f'http://backend/api/files/unverified/{point_id}'
    fp = open(f'{file_id}.{type_media}', 'rb')
    files = {'formFile': (f'{file_id}.{type_media}', fp, 'multipart/form-data', {})}
    response = requests.post(url, files=files)
    fp.close()
    status = response.status_code == requests.codes.ok
    return status


async def get_request_for_map(road_name, x, y):
    url = f'http://backend/api/roads/{road_name}/gasStations'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.get(url, params=location)
    return response.json()
