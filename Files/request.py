import json
import logging
import requests

domain = "http://213.171.29.33:5139"


async def get_road_and_region(longitude: float, latitude: float):
    """
    Вычисление ближайшей дороги и региона пользователя по координаам
    :param longitude: float: долгота
    :param latitude: float: ширина
    :return: {"roadName": "string", "regionName": "string"}
    """
    url = f"{domain}/api/v1/TgBot/location"
    data = {"Coordinates.Longitude": longitude, "Coordinates.Latitude": latitude}

    try:
        response = requests.get(url, params=data)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


# обьявления -------------------------------------------
async def get_request_audio(file_id: str):
    """
    Получение озвучки для обьявления
    :param file_id: str: id обьявления
    :return: Возвращает массив байт файла озвучки объявления с указанным ID
    """
    url = f"{domain}/api/v1/TgBot/advertisements/{file_id}/voice"
    try:
        response = requests.get(url)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response


# по области
async def get_advertisements_for_region(region_name: str):
    """
    Получение всех актуальных обьявлений, которые действуют для региона с указаным именем
    :param region_name: str: название региона, которое передается в url запроса
    :return: {"advertisements": [{"id": "uuid", "title": "string", "description": "string"}]}
    """
    url = f"{domain}/api/v1/TgBot/regions/{region_name}/advertisements"
    print(url)
    try:
        response = requests.get(url)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


# по дороге
async def get_request_urgent_message(road_name: str):
    """
    Получение всех актуальных обьявлений, которые действуют для дороги с указаным именем
    :param road_name: str: название дороги, которое передается в url запроса:
    :return: {"advertisements": [{"id": "uuid", "title": "string", "description": "string"}]}
    """
    url = f"{domain}/api/v1/TgBot/Roads/{road_name}/advertisements"
    try:
        response = requests.get(url)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


# ветка "сообщить" ---------------------------------------------
async def post_request_location_and_description(
    road_name: str,
    longitude: float,
    latitude: float,
    type_road: int,
    description: str,
    level: int,
):
    """
    Cоздает новую не верифицированную точку
    :param road_name: str: название дороги
    :param longitude: float: долгота
    :param latitude: float: широта
    :param type_road: int: тип точки(RoadDisadvantages/ThirdPartyIllegalActions)
    :param description: str: тип повреждения/ описание действия
    :param level: int: уровень доверия
    :return: {"pointId": str}
    """
    url = f"{domain}/api/v1/TgBot/UnverifiedPoints"
    data = {
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "type": type_road,
        "reliability": level,
        "description": description,
        "roadName": road_name,
    }

    try:
        response = requests.post(url, json=data)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 201:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


async def post_request_media(file_id: str, point_id: str, type_media: str) -> bool:
    """
    Прикрепляет файл (фото или видео) к не вверифицированной точке
    :param file_id: id файла, берущееся в качестве названия для файла
    :param point_id: id точки, к которой прикрепляется файл
    :param type_media: расширение файла (.mp4 / .jpg)
    :return: True (в случае статус кода 201) / False (в случает какой либо ошибки)
    """
    url = f"{domain}/api/v1/TgBot/UnverifiedPoints/{point_id}/file"
    with open(f"{file_id}.{type_media}", "rb") as fp:
        files = {
            "file": (
                f"{file_id}.{type_media}",
                fp,
                "image/jpeg" if type_media == "jpg" else "video/mp4",
                {},
            )
        }

    try:
        response = requests.post(url, files=files)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return False

    status = response.status_code == 201
    return status


# ветка "узнать" --------------------------------------------------
async def get_request_for_dots(
    road_name: str, longitude: float, latitude: float, point_type: str
):
    """
    Получение определенного кол-ва вер.точек на дороге в радиусе с типом
    :param road_name: название дороги
    :param longitude: долгота
    :param latitude: ширина
    :param point_type: тип отправляемой точки (Cafe, GasStation, CarService, RestPlace, InterestingPlace)
    :return: {"points": [{"name": str, "type": num, "coordinates": {"latitude": num, "longitude": num},"distanceFromUser": num}]}
    """
    url = f"{domain}/api/v1/TgBot/Roads/{road_name}/verifiedPoints/{point_type}"
    data = {
        "Coordinates.Longitude": longitude,
        "Coordinates.Latitude": latitude,
        "PointsCount": 10,
        "RadiusInKm": 50,
    }
    try:
        response = requests.get(url, params=data)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


async def get_approved_point(
        road_name: str, longitude: float, latitude: float
):
    """
    Получение всех подтвержденных точек в радиусе от пользователя
    :param road_name: название дороги
    :param longitude: долгота
    :param latitude: ширина
    :return: {"points": [{"name": str, "type": num, "coordinates": {"latitude": num, "longitude": num},"distanceFromUserInKm": num}]}
    """
    url = f"{domain}/api/v1/TgBot/Roads/{road_name}/approved-points"
    body = {
        "Coordinates.Longitude": longitude,
        "Coordinates.Latitude": latitude,
        "PointsCount": 10,
        "RadiusInKm": 50,
    }
    try:
        response = requests.get(url, params=body)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()


# ветка "гс" --------------------------------------------------
async def get_audio_label(path_to_file: str) -> json:
    url = "{domain}/classify/audio/road"
    file = {"file": open(path_to_file, "rb")}

    try:
        response = requests.post(url, files=file)
        logging.info(f"Запрос: {response}")
    except requests.exceptions.ConnectionError as error:
        logging.error(f"Не удалось обратиться к серверу: {error}")
        return None

    if response.status_code != 200:
        logging.warning(f"Возвращение со статусом {response.status_code}: {response.text}")
        return None

    return response.json()
