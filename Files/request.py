import requests


async def get_request_urgent_message(
        road_name: str
):
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/advertisements'
    response = requests.get(url)
    return response.json()


# ветка "сообщить" ---------------------------------------------
async def post_request_location_and_description(
        road_name: str,
        longitude: float,
        latitude: float,
        type_road: str,
        description: str = None
):
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/unverifiedPoints'
    data = {
        'description': description,
        'pointType': type_road,
        'longitude': longitude,
        'latitude': latitude,
        'roadName': road_name
    }
    response = requests.post(url, json=data)
    return response.json()


async def post_request_media(
        file_id: str,
        point_id: str,
        type_media: str
) -> bool:
    url = f'http://https://smiling-striking-lionfish.ngrok-free.app/api/files/unverified/{point_id}'
    fp = open(f'{file_id}.{type_media}', 'rb')
    files = {'formFile': (f'{file_id}.{type_media}', fp, 'multipart/form-data', {})}
    response = requests.post(url, files=files)
    fp.close()
    status = response.status_code == requests.codes.ok
    return status


# ветка "узнать" --------------------------------------------------
async def get_request_for_dots(
        road_name: str,
        longitude: float,
        latitude: float,
        point_type: str
):
    url = f'http://https://smiling-striking-lionfish.ngrok-free.app/api/roads/{road_name}/{point_type}'
    data = {
        'Coordinates.Longitude': longitude,
        'Coordinates.Latitude': latitude
    }
    response = requests.get(url, params=data)
    return response.json()
