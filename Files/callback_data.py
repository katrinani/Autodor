import json


data = {
    "all_type_actions": {
        "report_traffic_accident": "Дорожно-транспортные происшествия",
        "report_road_deficiencies": "Недостатки содержания дороги",
        "report_illegal_actions": "Противоправные действия 3-их лиц",
        "dangerous_situation": [
            "Куда звонить в экстренной ситуации?",
            "Угроза жизни и здоровья"],
        "recognize_meal": "Поесть",
        "recognize_gas_station": "Заправиться",
        "recognize_car_service": "Починить машину",
        "recognize_parking_lot": "Оставить машину",
        "recognize_attractions": "Интересные места"
    },
    "callback_type_road_deficiencies": [
            "Проломы, ямы, выбоины",
            "Трещины",
            "Гололёд",
            "Проблемы с разметкой"
        ],
    "callback_continue_or_return": ['continue', 'return'],
    "callback_map_for_meal": [f'location_meal_{i}' for i in range(10)],
    "callback_map_for_gas_station": [f'location_gas_station_{i}' for i in range(10)],
    "callback_map_for_car_service": [f'location_car_service_{i}' for i in range(10)],
    "callback_map_for_parking_lot": [f'location_parking_lot_{i}' for i in range(10)],
    "callback_map_for_attractions": [f'location_attractions_{i}' for i in range(10)],
    "callback_dangerous_situation": ['option_4', 'type_6']
}

with open('../recurses/text_for_message/callback_data.json', 'w') as file:
    json.dump(data, file)
