import json
from aiogram.utils.markdown import hide_link

data_for_mess = {
    "choice_of_area": """
    Добро пожаловать! Вас приветствует бот от Федерального Дорожного агенства. \
Прежде чем мы начнем, мне нужно узнать ваше нынешнее местоположение 
    """,
    "route_chelyabinsk": [
        "Челябинск-Москва",
        "Челябинск-Екатеринбург",
        "Челябинск-Троицк",
        "Челябинск-Курган"
    ],
    "route_kurgan": [
        "Курган-Москва",
        "Курган-Екатеринбург",
        "Курган-Троицк",
        "Курган-Челябинск"
    ],
    "route_choice": """
    Хорошо! Теперь подскажите пожалуйста по какой трассе Вы собираетесь ехать?
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
дороги, по возможности сфотографировать его и отправить геолокаци.
    """,
    "type_road_deficiencies": [
        "Колейность",
        "Просадки",
        "Проломы, ямы, выбоины",
        "Сдвиги покрыти",
        "Трещины",
        "Выкрашивание",
        "Крошение кромок",
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
    Осталось отправить геолокацию недостатка дороги:
    """,
    "end_road_deficiencies": """
    Спасибо! Мы учтем эту информацию
    """,
    "text_for_help_type": """
    Здесь Вы можете найти поянение к каждому типу недостатка содержания дороги 
    """,
    "type_definitions": [
        """Колейность
– это образование колеи на дороге, то есть продольный дефект покрытия, \
разрушение дороги вдоль линии наката по направлению движения автомобилей.""",
        """Просадки
– это дефекты в виде впадин со скошенными пологими краями.""",
        """Проломы, ямы, выбоины
В зависимости от степени серьезности дефекта так называют разрушение\
слоев дороги с резким изменением ее профиля.""",
        """Сдвиги покрытия
– это смещение слоев и другие пластические деформации, такие как \
наплывы и т. н. “гребенка” - это нарушение стандартов ровности автодороги, \
в основе которого лежит сдвиг материала покрытия.""",
        """Трещины
- дефект дорожного покрытия, возникающий в результате хрупкого разрушения \
асфальтобетонного или цементобетонного слоя, проявляющийся в виде \
нарушения сплошности покрытия.""",
        """Выкрашивание
– это поверхностное разрушение дорожного покрытия в результате отделения\
зерен минерального материала из покрытия.""",
        """Разрушение кромок
– разрушение краев покрытия в виде сетки трещин или откалывания материала.""",
        """Гололёд
– это слой плотного льда, образовавшийся на поверхности дороги.""",
        """Проблемы с разметкой на проезжей части,
- это отсутствие или плохое состояние разметки на проезжей части."""
    ]
}

with open('data_for_mess.json', 'w') as file:
    json.dump(data_for_mess, file)
