import requests, sys


# Преобразование координат в параметр ll, требуется без пробелов, через запятую и без скобок
def lon_lat(lon, lat):
    return str(lon) + "," + str(lat)


# Создание карты с соответствующими параметрами.
def load_map(
        longitude: float,
        latitude: float,
        list_dots: dict,
        color: str,
        key: str = "points"
):
    map_request = ("http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}&pt={pt}~".
                   format(ll=lon_lat(lon=longitude, lat=latitude),
                          z=9,
                          type="map",
                          pt=lon_lat(lon=longitude, lat=latitude) + ",pm2orgm"
                          )
                   )
    map_request += ""
    count = len(list_dots[key])
    for i in range(count):
        if i < (count - 1):
            lon = list_dots[key][i]['coordinates']['longitude']
            lat = list_dots[key][i]['coordinates']['latitude']
            map_request += lon_lat(lon=lon, lat=lat) + f',pm2{color}m{i + 1}' + '~'
        else:
            lon = list_dots[key][i]['coordinates']['longitude']
            lat = list_dots[key][i]['coordinates']['latitude']
            map_request += lon_lat(lon=lon, lat=lat) + f',pm2{color}m{i + 1}'

    response = requests.get(map_request)

    # Запись полученного изображения в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file
