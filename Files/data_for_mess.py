import json

data_for_mess = {
    "start_talk": """
    Добро пожаловать! Меня зовут Путеслав и я создан, чтобы сделать вашу дорогу более комфортной! \
Прежде чем мы начнем, скажите в каком формате вам удобно будет общаться?
    """,
    "mobile": """
    Конено! Вот файл, с помощью которого вы можете установить приложение и пользоваться им
    """,
    "choice_of_area": """
    Как будет удобно! Теперь давайте уточним ваше местоположение. В какой области вы находитесь?
    """,
    "route_choice": """
    Хорошо! Теперь подскажите пожалуйста по какой трассе Вы собираетесь ехать?
    """,
    "good_situation": """
    На данной дороге не выявлено неполадок
    """,
    "choose_action": """
    Отлично! Вы хотели бы о чём-то сообщить или что-то узнать?
    """,
    "choose_report": [
        "Дорожно-транспортное происшествие",
        "Недостатки содержания дороги",
        "Противоправные действия 3-их лиц",
        "Угроза жизни и здоровью",
    ],
    "text_report": """
    Хорошо! О чем именно Вы хотите сообщить
    """,
    "traffic_accident": """
    Понял. Вам нужно обратиться в ГИБДД. Вот список номеров:
Челябинская область:
    +7(351)251-03-21
    +7(351)256-16-84
    +7(351)256-28-08
Курганская область:
    +7(3522)25-64-90
    """,
    "road_deficiencies": """
    Принял. Тогда Вам нужно выбрать тип недостатка содержания \
дороги, по возможности сфотографировать его и отправить геолокацию.
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
    "photo_road_deficiencies": """
    Теперь пожалуйста отправьте фотографию недостатка содержания дороги:
    """,
    "locate_road_deficiencies": """
    Сначала Вам нужно отправить геолокацию недостатка дороги:
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
       - Угрозе жизни и здоровью
    """,
    "bad_situation": """
    Хмм что-то пошло не так, попробуйте отправить еще раз.
    """
}

with open('../recurses/text_for_message/data_for_mess.json', 'w') as file:
    json.dump(data_for_mess, file)
