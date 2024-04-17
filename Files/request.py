import requests


async def get_request_urgent_message(
        road_name: str
):
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/Roads/{road_name}/advertisements'
    response = requests.get(url)
    return response.json()


# ветка "сообщить" ---------------------------------------------
async def post_request_location_and_description(
        road_name: str,
        longitude: float,
        latitude: float,
        type_road: str,
        description: str
):
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/UnverifiedPoints'
    data = {
        'point': {
            'type': type_road,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            'description': description
        },
        'roadName': road_name
    }
    response = requests.post(url, json=data)
    return response.json()


async def post_request_media(
        file_id: str,
        point_id: str,
        type_media: str
) -> bool:
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/UnverifiedPoints/{point_id}/file'
    fp = open(f'{file_id}.{type_media}', 'rb')
    files = {'file': (f'{file_id}.{type_media}', fp, 'multipart/form-data', {})}
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
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/Roads/{road_name}/verifiedPoints/{point_type}'
    data = {
        'Coordinates.Longitude': longitude,
        'Coordinates.Latitude': latitude
    }
    response = requests.get(url, params=data)
    return response.json()
