from aiogram.fsm.state import State, StatesGroup


class ProfileStatesGroup(StatesGroup):
    text_or_voice = State()

    input_voice = State()
    go_to_road_deficiencies = State()
    voice_right_or_not = State()

    input_description_for_illegal_actions = State()
    input_description_for_road_deficiencies = State()
    input_description_for_traffic_accident = State()
    input_description_for_road_block = State()

    input_location = State()
    advertisements = State()
    report_or_recognize = State()
    report = State()
    recognize = State()

    input_photo_for_road_deficiencies = State()
    input_photo_for_illegal_actions = State()

    output_text_for_road_deficiencies = State()

    output_points_for_meal = State()
    output_points_for_gas_station = State()
    output_points_for_car_service = State()
    output_points_for_parking_lot = State()
    output_points_for_attractions = State()