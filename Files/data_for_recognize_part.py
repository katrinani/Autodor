import json

data_for_mess = {
    "recognize": """
    Хорошо. О чем Вы хотите узнать?
    """,
    "questions_for_recognize": [
        "Где можно поесть?",
        "Где можно заправиться?",
        "Где я могу починить машину?",
        "Где я могу оставить машину на время?",
        "Что меня ждет на дорге?",
        "Что интересного есть по пути?",
        "Куда звонить в экстренной ситуации?",
    ],
    "start_and_send_location": """
    Понял! Для этого вам нужно отправить свою нынешнюю локацию
    """,
    "choose_meal": """
    Отлично. Теперь выберите удобное для Вас место, чтобы поесть:
    """,
    "choose_gas_station": """
    Отлично. Теперь выберите удобное для Вас место заправки:
    """,
    "choose_car_service": """
    Отлично. Теперь выберите удобный для Вас автосервис:
    """,
    "choose_parking_lot": """
    Отлично. Теперь выберите удобное для Вас место парковки:
    """,
    "choose_attractions": """
    Отлично. Теперь выберите интересное Вам место
    :
    """
}

with open('../base/data_for_recognize.json', 'w') as file:
    json.dump(data_for_mess, file)
