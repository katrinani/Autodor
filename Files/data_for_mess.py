import json

data_for_mess = {
    "start_talk": """
    Добро пожаловать! Меня зовут Путеслав и я создан, чтобы сделать вашу дорогу более комфортной!
Прежде чем мы начнем, нам нужно определить где вы едете. Отправте свою геолокацию пожалуйста
    """,
    "text_or_voice": """
    Скажите в каком формате вам удобно будет общаться?
    """,
    "good_situation_for_region": """
    Обьявлений для Вашего региона нет, всё хорошо!
    """,
    "good_situation_for_route": """
    Обьявлений для Вашей дороги нет, всё хорошо!
    """,
    "choose_action": """
    Отлично! Вы хотели бы о чём-то сообщить или что-то узнать?
    """,
    "choose_report": [
        "Дорожно-транспортное происшествие",
        "Недостатки содержания дороги",
        "Противоправные действия 3-их лиц",
        "Преграда на дороге",
    ],
    "text_report": """
    Хорошо! О чем именно Вы хотите сообщить?
    """,
    "traffic_accident": """
    Понял. Тогда пожалуйста опишите, что с вами произошло:
    """,
    "road_deficiencies": """
    Принял. Тогда Вам нужно выбрать тип недостатка содержания \
дороги, по возможности сфотографировать его.
""",
    "type_road_deficiencies": [
        "Проломы, ямы, выбоины",
        "Трещины",
        "Гололёд",
        "Проблемы с разметкой"
    ],
    "text_for_type_road_deficiencies": """
    Пожалуйста выберите тип недостаток содержания из предложенных:
    """,
    "photo_or_not": """
    Хотите ли вы отправить фото или видео?
    """,
    "photo_road_deficiencies": """
    Теперь пожалуйста отправьте фотографию недостатка содержания дороги:
    """,
    "lack_of_photo": """
    Хорошо. Мы учтем эту информацию
    """,
    "end_road_deficiencies": """
    Спасибо! Мы учтем эту информацию
    """,
    "instructions_for_contact": """
    Понял. Тогда вам нужно сфотографировать или записать видео с участием 3-го лица, \
совершающего противоправное действие, и добавить краткое описание. Начнем!
    """,
    "action_description": """
    Сейчас напишите пожалуйста краткое описание :
    """,
    "media_of_illegal_actions": """
    Принял. Осталось только отправить видео или фото противоправного действия:
    """,
    "dangerous_situation": """
    Сюда вы можете обратиться при возникновении экстренной ситуации:
В России номер 112 является единым номером вызова служб экстренного реагирования:
    - пожарной охраны;
    - реагирования в чрезвычайных ситуациях;
    - полиции;
    - скорой медицинской помощи;
    - аварийной службы газовой сети;
    - «Антитеррор».
Единый телефон пожарных и спасателей – 101.
    """,
    "voice_requirements": """
    Понял! Вы можете отправить голосовае сообщение для облегчения взаимодействия с ботом. Попробуйте!  
Нужно лишь сказать на какой дороге вы едете и что вы хотите сделать.
    Узнать:
       - Где можно поесть?
       - Где можно заправиться?
       - Где я могу починить машину?
       - Где я могу оставить машину на время?
       - Что интересного есть по пути?
       - Куда звонить в экстренной ситуации?
    Сообщить о:
       - Дорожно-транспортном происшествии
       - Недостатках содержания дороги
       - Противоправных действиях 3-их лиц
       - Преграде на дороге
    """,
    "bad_situation": """
    Хмм.. Что-то пошло не так, попробуйте отправить еще раз.
    """,
}

with open('/usr/src/app/recurses/text_for_message/data_for_mess.json', 'w') as file:
    json.dump(data_for_mess, file)
