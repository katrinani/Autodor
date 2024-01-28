import requests


async def post_request_for_road_deficiencies(road_name, x, y):
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/unverified'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.post(url, json=location)
    return response.json()


async def post_request_for_photo(file_id, point_id):
    url = f'http://192.168.100.5:5137/api/files/unverified/{point_id}'
    fp = open(f'{file_id}.jpg', 'rb')
    files = {'formFile': (f'{file_id}.jpg', fp, 'multipart/form-data', {})}
    response = requests.post(url, files=files)
    fp.close()
    status = response.status_code == requests.codes.ok
    return status


async def get_request_for_map(road_name, x, y):
    url = f'http://192.168.100.5:5137/api/roads/{road_name}/gasStations'
    location = {'x': x, 'y': y, 'roadName': ''}
    response = requests.get(url, params=location)
    return response.json()
