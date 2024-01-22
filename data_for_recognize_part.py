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
    "link": """
    <iframe src="https://yandex.ru/map-widget/v1/?um=constructor%3A9ce229d45f3f0b61769a93b986517dd\
    a8e2753bd0ec478665b3285d3b65aa0b4&amp;source=constructor" width="500" height="400" frameborder="0"></iframe>
    """

}

with open('data_for_recognize.json', 'w') as file:
    json.dump(data_for_mess, file)
