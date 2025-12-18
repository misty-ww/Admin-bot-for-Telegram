from aiogram.fsm.state import StatesGroup, State
class stateW(StatesGroup):
    waiting_name_file = State()
    waiting_file = State()
    waiting_info_file = State()


    waiting_label_link = State()
    waiting_name_link = State()
    waiting_link = State()
    waiting_info_link = State()

    waiting_file_hand = State()
    waiting_name_file_hand = State()
    waiting_info_file_hand = State()

    waiting_text_hand = State()

    waiting_new_time = State()

    waiting_id_delete = State()

    waiting_message_from_tgc = State()

    waiting_mess_for_tgc = State()
    
    waiting_id_mess_for_delete_tgc = State()

    waiting_new_time_tgc = State()

