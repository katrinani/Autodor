import requests


async def get_all_regions():
    """
    На вход ничего не идет
    :return: {"regions": [{"name": "string"}]}
    """
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/regions'
    response = requests.get(url)
    return response.json()


async def get_all_roads():
    """
    На вход ничего не идет
    :return:  {"roads": [{"roadName": "string"}]}
    """
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/roads'
    response = requests.get(url)
    return response.json()


# обьявления -------------------------------------------
# по области
async def get_advertisements_for_region(
        region_name: str
):
    """
    :param region_name:  название региона, которое передается в url запроса
    :return: {"advertisements": [{
      "title": "string",
      "description": "string", // может отсутствовать
      "regionName": "string"
        }]}
    """
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/regions/{region_name}/advertisements'
    response = requests.get(url)
    return response.json()


# по дороге
async def get_request_urgent_message(
        road_name: str
):
    """
    :param road_name: название дороги, которое передается в url запроса:
    :return: {"advertisements": [{
      "title": "string",
      "description": "string", // может отсутствовать
      "regionName": "string" // будет null
        }]}
    """
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
    """
    :param road_name: название дороги
    :param longitude: долгота
    :param latitude: широта
    :param type_road: тип точки(RoadDisadvantages/ThirdPartyIllegalActions)
    :param description: тип повреждения/ описание действия
    :return: {"pointId": str}
    """
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/UnverifiedPoints'
    data = {
        'point': {
            'type': type_road,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            },
            "road": {
                'roadName': road_name
            }
        },
        'description': description
    }
    response = requests.post(url, json=data)
    return response.json()


async def post_request_media(
        file_id: str,
        point_id: str,
        type_media: str
) -> bool:
    """
    :param file_id: id файла, берущееся в качестве названия для файла
    :param point_id: id точки, к которой прикрепляется файл
    :param type_media: расширение файла (.mp4 / .jpg )
    :return: True (в случае статус кода 200) / False (в случает какой либо ошибки)
    """
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
    """
    :param road_name: название дороги
    :param longitude: долгота
    :param latitude: ширина
    :param point_type: тип отправляемой точки (Cafe, GasStation, CarService, RestPlace, InterestingPlace)
    :return: {"points": [{"name": str, "type": num, "coordinates": {"latitude": num, "longitude": num},
    "distanseFromUser": num}]}
    """
    url = f'https://smiling-striking-lionfish.ngrok-free.app/api/Roads/{road_name}/verifiedPoints/{point_type}'
    data = {
        'Coordinates.Longitude': longitude,
        'Coordinates.Latitude': latitude,
        'PointsCount': 10,  # максимальное кол-во точек
        'Radius': 50  # радиус для отправленных точек
    }
    response = requests.get(url, params=data)
    return response.json()
