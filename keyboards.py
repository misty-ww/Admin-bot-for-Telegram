from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
kb_create = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📁Создать файл для auto рассылки", callback_data="file")], 
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
kb_create2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📁Создать файл для auto рассылки", callback_data="file"), 
         InlineKeyboardButton(text="🔗Создать ссылку", callback_data="link")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
start = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💬 Рассылка в лс бота", callback_data="dm_mode")], 
         [InlineKeyboardButton(text="💬 Рассылка в тгк", callback_data="tg_mode")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
dm_mode = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📁 Все файлы для рассылки", callback_data="all_file")], 
         [InlineKeyboardButton(text="Создать файл", callback_data="add_file"),
         InlineKeyboardButton(text="Удалить файл", callback_data="delete_file")],
        [InlineKeyboardButton(text="⏰ Изменить время рассылки", callback_data="change_time")], 
         [InlineKeyboardButton(text="Пауза", callback_data="pause_time"),
         InlineKeyboardButton(text="Возобновить", callback_data="resume_time")],
         [InlineKeyboardButton(text="💬 Рассылка в тгк",callback_data="tg_mode")],
         [InlineKeyboardButton(text="✋ Ручная рассылка",callback_data="hand_send")],
         [InlineKeyboardButton(text="📊 Статистика",callback_data="stat")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
tg_mode = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💡 Подключить тгк для расылки", callback_data="add_tgc")], 
        [InlineKeyboardButton(text="📝 Все сообщения для рассылки", callback_data="all_mes_tg")], 
         [InlineKeyboardButton(text="Создать сообщение", callback_data="add_mes_tg"),
         InlineKeyboardButton(text="Удалить сообщение", callback_data="delete_mes_tg")],
        [InlineKeyboardButton(text="⏰ Изменить время рассылки", callback_data="change_time_tg")], 
         [InlineKeyboardButton(text="Пауза", callback_data="pause_time_tg"),
         InlineKeyboardButton(text="Возобновить", callback_data="resume_time_tg")],
         [InlineKeyboardButton(text="💬 Рассылка в лс бота",callback_data="dm_mode")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
kb_cencel = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)
kb_cencel_tgMode = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="💬 Обратно в панель",callback_data="tg_mode")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)

kb_send = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📁Отправить файл", callback_data="file_send")], 
         [InlineKeyboardButton(text="🔗Отправить ссылку или просто ✏️текст", callback_data="link_send")],
         [InlineKeyboardButton(text="❌ Отменить",callback_data="cencel")]
    ]
)