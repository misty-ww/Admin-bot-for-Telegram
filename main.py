from aiogram import Bot, Dispatcher,types,F
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import config
import states 
import keyboards
from func import *
import secrets
bot = Bot(token=config.token)
dp = Dispatcher()
apscheduler = AsyncIOScheduler(timezone="Europe/Moscow")


#РЕЖИМ РАССЫЛКИ В ТГК
@dp.callback_query(F.data == "tg_mode")
async def tg_mode_(callback:CallbackQuery,state:FSMContext):
    if not admin(config.admins, callback.from_user.id):
        await callback.message.answer(
        "❌ Нет прав на эту команду!"
    )
        await callback.answer()
        return
    await callback.message.answer(config.tgc,
                                  parse_mode='HTML',
                                  reply_markup=keyboards.tg_mode)
    await callback.answer()


#ПОДКЛЮЧЕНИЕ ТГК 
@dp.callback_query(F.data == "add_tgc")
async def add_tgc_(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("""
❗️ <b>ДАННЫЙ БОТ ДОЛЖЕН БЫТЬ ДОБАВЛЕН В ВАШ ТГК И ИМЕТЬ ПРАВА АДМИНИСТРАТОРА</b>

🧩 <b>Вам необходимо:</b>
<i>1.Добавить бота в ваш тгк и выдать права администратора</i>                                        
<i>2.Перекинуть в этот чат текстовое сообщение из вашего тгк</i>

🎯 <i>После этого бот получит возможность рассылать сообщения в ваш тгк</i>                                                                                                                            
""",
                                  parse_mode='HTML',
                                  reply_markup=keyboards.kb_cencel_tgMode)
    await state.set_state(states.stateW.waiting_message_from_tgc)
    await callback.answer()
@dp.message(states.stateW.waiting_message_from_tgc)
async def waiting_message_from_tgc_(message:types.Message,state:FSMContext):
    if message.forward_from_chat:
        chat = message.forward_from_chat
        chat_id = chat.id
        name = chat.title
    elif message.chat.type == "channel":
        chat_id = message.chat.id
        name = message.chat.title
    else:
        chat_id = None
        message.answer("❗️ <i>Произошла ошибка</i>",
                       parse_mode='HTML',
                       reply_markup=keyboards.start)
        return
    baze = {"chat_id": chat_id}
    isOk = await get_Json("w",baze)
    if isOk is None:
        await message.answer("❗️ <i>Произошла ошибка</i>",
                       parse_mode='HTML',
                       reply_markup=keyboards.start)
        return
    if not isOk == "Load":
        await message.answer("❗️ <i>Произошла ошибка</i>",
                       parse_mode='HTML',
                       reply_markup=keyboards.start)
        return
    await message.answer(f"""
👍 <i>Канал для рассылки сохранен/обновлен</i>
👀 <b>Имя тгк:</b> {name}
🆔 <b>Id:</b> {chat_id}
                         """,
                         parse_mode='HTML',
                         reply_markup=keyboards.start)
    await state.clear()


#ДОБАВЛЕНИЕ СМС ДЛЯ РАССЫЛКИ В ТГК
@dp.callback_query(F.data == "add_mes_tg")
async def add_mes_tg_(callback:CallbackQuery,state:FSMContext):
    if not admin(config.admins, callback.from_user.id):
        await callback.message.answer(
        "❌ Нет прав на эту команду!"
    )
        await callback.answer()
        return
    d = await get_Json("r",None)
    if d is None:
        await callback.message.answer("❗️ 1<i>Произошла ошибка</i>",
                                      parse_mode='HTML',
                                      reply_markup=keyboards.start)
        await callback.answer()
        return
    chat_id = d["chat_id"]
    if not chat_id:
        await callback.message.answer("❗️ 2<i>Канал для рассылки не найден</i>",
                                          parse_mode='HTML',
                                          reply_markup=keyboards.start)
        await callback.answer()
        return
    await callback.message.answer("<i>Напиши текст сообщения для рассылки (Можно использовать HTML тэги)</i>",
                                  parse_mode='HTML',
                                  reply_markup=keyboards.kb_cencel_tgMode)
    await state.update_data(chat_id = chat_id)
    await state.set_state(states.stateW.waiting_mess_for_tgc)
    await callback.answer()
@dp.message(states.stateW.waiting_mess_for_tgc)
async def waiting_mess_for_tgc_(message:types.Message,state:FSMContext):
    if message.text:
        text = message.text
        if len(text) > 4096:
            await message.answer("❗️ <i>Слишком длинный текст</i>\n❗️ <b>Пиши до 4096 символов</b>",
                                     parse_mode='HTML',
                                     reply_markup=keyboards.start)
            return
        isOk = await input_mes_tgc(text)
        if isOk == False:
            await message.answer("❗️ <i>Произошла ошибка</i>",
                                     parse_mode='HTML',
                                     reply_markup=keyboards.start)
            return
        await message.answer(f"""
<i>Сообщение для рассылки в тгк сохранено</i>
                             
<b>Текст:</b> [{text}]                           
""",
parse_mode='HTML',
reply_markup=keyboards.start)
        await state.clear()
#ПРОСМОТР ВСЕХ СООБЩЕНИЙ ДЛЯ РАССЫЛКИ
@dp.callback_query(F.data == "all_mes_tg")
async def all_mes_tg_(callback:CallbackQuery):
    base = await check_all_mess_tgc()
    if base is None:
        await callback.message.answer("❗️ <i>Сообщения для рассылки не найдены</i>",
                                          parse_mode='HTML',
                                          reply_markup=keyboards.start)
        await callback.answer()
        return
    textM = "💌 <i>Все сообщения для рассылки:</i> \n"
    for i,data in enumerate(base,1):
        idM,text,date = data
        textM +=f"""
📌 {i}. <b>Id:</b> {idM}
✏️ <b>Текст:</b> [{text}]
⏳ <b>Дата создания:</b> <i>{date}</i>
"""
    await callback.message.answer(textM,
                                  parse_mode='HTML',
                                  reply_markup=keyboards.start)
    await callback.answer()
#Удаление соо из рассылки
@dp.callback_query(F.data == "delete_mes_tg")
async def delete_mes_tg_(callback:CallbackQuery,state:FSMContext):
    base = await check_all_mess_tgc()
    if base is None:
        await callback.message.answer("❗️ <i>Сообщения для рассылки не найдены</i>",
                                          parse_mode='HTML',
                                          reply_markup=keyboards.start)
        await callback.answer()
        return
    textM = "💌 <i>Все сообщения для рассылки:</i> \n"
    for data in base:
        idM,text,date = data
        textM +=f"""
📌 <b>Id:</b> <code>{idM}</code>
✏️ <b>Текст:</b> [{text}]
⏳ <b>Дата создания:</b> <i>{date}</i>
"""
    await callback.message.answer(textM,
                                  parse_mode='HTML',
                                  reply_markup=keyboards.start)
    await callback.message.answer("<i>Напиши id сообщения, которое удалить из рассылки</i>",
                                  parse_mode='HTML',
                                  reply_markup=keyboards.kb_cencel_tgMode)
    await state.set_state(states.stateW.waiting_id_mess_for_delete_tgc)
    await callback.answer()
@dp.message(states.stateW.waiting_id_mess_for_delete_tgc)
async def waiting_id_mess_for_delete_tgc_(message:types.Message,state:FSMContext):
    if message.text:
        id = message.text
        isOk = await delete_mes_tgc(id)
        if isOk == False:
            await message.answer("❗️ <i>Произошла ошибка</i>",
                                     parse_mode='HTML',
                                     reply_markup=keyboards.start)
            await state.clear()
            return
        await message.answer(f"✅ <i>Сообщение с id: {id} успешно удалено из рассылки</i>",
                             parse_mode='HTML',
                             reply_markup=keyboards.start)
        await state.clear()

#РАБОТА С ПАРАМЕТРАМИ ТГК РАССЫЛКИ
@dp.callback_query(F.data == "change_time_tg")
async def change_time_tg_(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("<i>✏️Введи новое время рассылки в таком формате</i>\n20:00\n05:25\n09:30",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
    await state.set_state(states.stateW.waiting_new_time_tgc)
    await callback.answer()
@dp.message(states.stateW.waiting_new_time_tgc)
async def new_time(message:types.Message,state:FSMContext):
    time = message.text
    new = time.split(":")
    if len(new) != 2:
        message.answer("❌НЕКОРЕКТНОЕ ВРЕМЯ, ВВЕДИ ЗАНОВО")
        return
    houre = new[0]
    minute = new[1]
    if not houre.isdigit() or not minute.isdigit():
        message.answer("❌НЕКОРЕКТНОЕ ВРЕМЯ, ВВЕДИ ЗАНОВО")
        return
    apscheduler.remove_job("tgc_message")
    apscheduler.add_job(message_to_tgc,
                        CronTrigger(hour=houre,minute=minute),
                        id="tgc_message")
    await message.answer(f"⌛️Время auto рассылки изменено на <b>{houre}:{minute}</b>\nПри перезапуске бота оно будет уставновлено <i>на 19:00 по умолчания</i>",
                         parse_mode='HTML')
    await state.clear()
@dp.callback_query(F.data == "pause_time_tg")
async def pause_time_tg_(callback:CallbackQuery):
    apscheduler.pause_job("tgc_message")
    await callback.message.answer("⌛️ <i>Рассыклка в тгк поставлена на паузу</i>",
                                  parse_mode='HTML')
    await callback.answer()
@dp.callback_query(F.data == "resume_time_tg")
async def resume_time_tg_(callback:CallbackQuery):
    apscheduler.resume_job("tgc_message")
    await callback.message.answer("⌛️ <i>Рассыклка в тгк возобновлена</i>",
                                  parse_mode='HTML')
    await callback.answer()


#f РАССЫЛКИ ДЛЯ tgc
async def message_to_tgc():
    mess = await asyncio.to_thread(get_1_mes_tgc)
    if mess is None:
        await bot.send_message(chat_id=config.admin,
                               text="❗️ <i>Нет сообщений для рассылки</i> \n<b>Рассылка в тгк не произведена</b>",
                               parse_mode='HTML')
        return
    id_m, text_m = mess
    chatIdData = await get_Json("r",None)
    if not chatIdData:
            await bot.send_message(
                chat_id=config.admin,
                text="❗️ <b>Ошибка: не найден ID чата для рассылки</b>",
                parse_mode='HTML'
            )
            return
    chatId = chatIdData["chat_id"]
    try:
        await bot.send_message(chat_id=chatId,
                           text=text_m,
                           parse_mode='HTML')
    except Exception as e:
            # Более информативное сообщение об ошибке
            error_msg = f"❗️ <b>Ошибка отправки в ТГК:</b>\n<code>{e}</code>"
            await bot.send_message(
                chat_id=config.admin,
                text=error_msg,
                parse_mode='HTML'
            ) 
            return
    isOk = await delete_mes_tgc(id_m)
    if not isOk:
        await bot.send_message(chat_id=config.admin,
                               text="❗️ <b>Произошла ошибка: сообщение не удалено из дальнейшей рассылки</b>",
                               parse_mode='HTML')
        return
    await bot.send_message(chat_id=config.admin,
                               text=f"""
📌 Сообщение с текстом: 

✏️ [{text_m[:100]}{'...' if len(text_m) > 100 else ''}]

✅ Отпралено в тгк с Id: {chatId}
💣 И удалено из рассылки
""",
                               parse_mode='HTML')
    

#РЕЖИМ РАССЫЛКИ В ЛС БОТА
@dp.callback_query(F.data == "dm_mode")
async def tg_mode_(callback:CallbackQuery,state:FSMContext):
    if not admin(config.admins, callback.from_user.id):
        await callback.message.answer(
        "❌ Нет прав на эту команду!"
    )
        await callback.answer()
        return
    await callback.message.answer(config.dm,
                                  parse_mode='HTML',
                                  reply_markup=keyboards.dm_mode)
    await callback.answer()



#СТАТИСТИКА
@dp.callback_query(F.data == "stat")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌ Нет прав на эту команду!"
    )
        await callback.answer()
        return
    users_ok = await asyncio.to_thread(get_users,"okey")
    if users_ok:
        num_ok = 0
        for user_ok in users_ok:
            num_ok +=1
    users_skip = await asyncio.to_thread(get_users,"skip")
    num_skip = 0
    if users_skip:
        for user_skip in users_skip:
            num_skip +=1
    num_all = num_skip+num_ok
    files = await asyncio.to_thread(get_id_files)
    num_files = 0
    if files:
        for file in files:
            num_files +=1
    text = f"""
<b>📊 СТАТИСТИКА:</b>

👥 <i>Всего пользователей:</i> {num_all}
✅ <i>Активных:</i> {num_ok}
❌ <i>В ЧС:</i> {num_skip}

<i>📁Всего файлов для рассылки:</i> {num_files}
"""
    await callback.message.answer(text,
                         parse_mode='HTML')
    await callback.answer()


#УДАЛЕНИЕ ФАЙЛА ИЗ РАССЫЛКИ
@dp.callback_query(F.data == "delete_file")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    files = await asyncio.to_thread(get_id_files)
    if not files:
        await callback.message.answer("📛 <b>Нет файлов для рассылки</b>",
                         parse_mode='HTML')
        await callback.answer()
        return
    await callback.message.answer("📁 <b>Файлы для auto рассылки:</b>",
                         parse_mode='HTML')
    text = f""
    for file in files:
        idf,file_id,file_name,file_info = file
        text += f"""
<i>⚙️ Уникальный id:</i>  {idf}
📌 <i>Имя фала:</i> {file_name}
"""
    await callback.message.answer(text,
                         parse_mode='HTML')
    await callback.message.answer("<i>Напиши id одного файла для удаления</i>",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
    await state.set_state(states.stateW.waiting_id_delete)
    await callback.answer()
@dp.message(states.stateW.waiting_id_delete)
async def id_delete(message:types.Message,state:FSMContext):
    idf = message.text.strip()
    isDelete = await asyncio.to_thread(delete_file,idf)
    isDeleteUser = await asyncio.to_thread(delete_file_user,idf)
    if not isDelete:
        await message.answer("📛 Произошла ошибка\nВведи id заново",
                             reply_markup=keyboards.kb_cencel)
        return
    await message.answer(f"💣<i>Файл с id:{idf} удален</i>",
                         parse_mode='HTML')
    await state.clear()


#ПРОСМОТР ВСЕХ ФАЙЛОВ ДЛЯ РАССЫЛКИ
@dp.callback_query(F.data == "all_file")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    files = await asyncio.to_thread(get_id_files)
    if not files:
        await callback.message.answer("📛 <b>Нет файлов для рассылки</b>",
                         parse_mode='HTML')
        await callback.answer()
        return
    await callback.message.answer("<b>Файлы для auto рассылки:</b>",
                         parse_mode='HTML')
    text = f""
    num = 0
    for file in files:
        idf,file_id,file_name,file_info = file
        text += f"""
⚙️ <i>Уникальный id:</i>  {idf}
🔑 <i>Уникальный Tg_id:</i>  {file_id}
📌 <i>Имя файла:</i> {file_name}
ℹ️ <i>Информация о файле</i>  {file_info}
"""
        num +=1
    await callback.message.answer(text,
                         parse_mode='HTML')
    await callback.message.answer(f"<i>Всего файлов {num}</i>",
                         parse_mode='HTML')
    await callback.answer()


#РАБОТА С ПАРАМЕТРАМИ РАССЫЛКИ dmBOT
@dp.callback_query(F.data == "change_time")
async def stattime(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    await callback.message.answer("<i>✏️Введи новое время рассылки в таком формате</i>\n20:00\n05:25\n09:30",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
    await state.set_state(states.stateW.waiting_new_time)
    await callback.answer()
@dp.message(states.stateW.waiting_new_time)
async def new_time(message:types.Message,state:FSMContext):
    time = message.text
    new = time.split(":")
    if len(new) != 2:
        message.answer("❌НЕКОРЕКТНОЕ ВРЕМЯ, ВВЕДИ ЗАНОВО")
        return
    houre = new[0]
    minute = new[1]
    if not houre.isdigit() or not minute.isdigit():
        message.answer("❌НЕКОРЕКТНОЕ ВРЕМЯ, ВВЕДИ ЗАНОВО")
        return
    apscheduler.remove_job("dailyId")
    apscheduler.add_job(daily_massage,
                        CronTrigger(hour=houre,minute=minute),
                        id="dailyId")
    await message.answer(f"⌛️Время auto рассылки изменено на <b>{houre}:{minute}</b>\nПри перезапуске бота оно будет уставновлено <i>на 19:00 по умолчания</i>",
                         parse_mode='HTML')
    await state.clear()
@dp.callback_query(F.data == "pause_time")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    apscheduler.pause_job("dailyId")
    await callback.message.answer("⌛️Рассылка поставлена на паузу")
    await callback.answer()
@dp.callback_query(F.data == "resume_time")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    apscheduler.resume_job("dailyId")
    await callback.message.answer("⌛️Рассылка началась")
    await callback.answer()


@dp.message(Command("admin"))
async def commands(message:types.Message):
    id = message.from_user.id
    if not admin(config.admins, id):
        await message.answer(
        "❌Нет прав на эту команду!"
    )
        return
    await message.answer("🕹 <i>Выбери режим</i>",
                         parse_mode='HTML',
                         reply_markup=keyboards.start)

#РУЧНАЯ РАССЫЛКА
@dp.callback_query(F.data == "hand_send")
async def stat(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("<i>Выбери</i>",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_send)
    await callback.answer()   


#РУЧНАЯ РАССЫЛКА text/link
@dp.callback_query(F.data == "link_send")
async def hand_text(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("<i>✏️Введи ссылку/сообщение для рассылки\nОтправь в этот чат\nОно автоматически разошлется пользоватлям</i>",
                            parse_mode='HTML',
                            reply_markup=keyboards.kb_cencel)
    await state.set_state(states.stateW.waiting_text_hand)
@dp.message(states.stateW.waiting_text_hand)
async def text_wait_hand(message:types.Message,state:FSMContext):
    users = await asyncio.to_thread(get_users,"okey")
    num = 0
    if users is None:
        await bot.send_message(chat_id=config.admin,text="<i>❌Нет пользователей для рассылки</i>",
                               parse_mode='HTML')
        await state.clear()
        return
    for user in users:
        user = user[0]
        await bot.send_message(chat_id=user,
                               text=f"{message.text}",
                               parse_mode='HTML')
        num +=1
        await message.answer(f"📬Сообщение отправлено для {user}")
        await asyncio.sleep(5)
    await message.answer(f"<i>💌Рассылка сообщения:\n[{message.text}]\n\nДля {num} пользователей завершина</i>",
                         parse_mode='HTML')
    await state.clear()


#РУЧНАЯ РАССЫЛКА file
@dp.callback_query(F.data == "file_send")
async def hand_file(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("<i>📩Отправь файл</i>",
                            parse_mode='HTML',
                            reply_markup=keyboards.kb_cencel)
    await state.set_state(states.stateW.waiting_file_hand)
    await callback.answer()
@dp.message(states.stateW.waiting_file_hand)
async def new_fileH(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    await state.update_data(file_id = file_id)
    await state.set_state(states.stateW.waiting_name_file_hand)
    await message.answer(
        "📩Введи <b>имя</b> для файла",
        parse_mode='HTML',
        reply_markup=keyboards.kb_cencel
    )
@dp.message(states.stateW.waiting_name_file_hand)
async def nameFileH(message: types.Message, state: FSMContext):
    name_file = message.text
    await state.update_data(name_file=name_file)
    await state.set_state(states.stateW.waiting_info_file_hand)
    await message.answer(
        "📩Введи <b>описание</b> для файла, которое будет читать пользователь",
        parse_mode='HTML',
        reply_markup=keyboards.kb_cencel
    )
@dp.message(states.stateW.waiting_info_file_hand)
async def infoFileH(message: types.Message, state: FSMContext):
    info_file = message.text
    await state.update_data(info_file=info_file)
    data = await state.get_data()
    users = await asyncio.to_thread(get_users,"okey")
    if users is None:
        await bot.send_message(chat_id=config.admin,text="<i>❌Нет пользователей для рассылки</i>",
                               parse_mode='HTML')
        await state.clear()
        return
    num = 0
    for user in users:
        user = user[0]
        num +=1
        await bot.send_document(chat_id=user,document=data['file_id'],caption=f"""
<b>{data['name_file']}</b>\n\n<i>{data['info_file']}</i>
""",
parse_mode='HTML')
        await message.answer(f"📬Файл отправлен для {user}")
        await asyncio.sleep(5)
    await message.answer(f"💌Рассылка файла {data['name_file']} завершена для {num} пользователей \n/commands")
    await state.clear()


#f РАССЫЛКИ
async def daily_massage():
    users = await asyncio.to_thread(get_users,"okey")
    if users is None:
        await bot.send_message(chat_id=config.admin,text="<i>❌Нет пользователей для рассылки</i>",
                               parse_mode='HTML')
        return
    files = await asyncio.to_thread(get_id_files)
    if files is None:
        await bot.send_message(chat_id=config.admin,text="<i>❌Нет файлов для рассылки</i>",
                               parse_mode='HTML')
        return
    lenf = len(files)
    print(lenf)
    user_i = 0
    isGet = {}
    for user in users:
        user = user[0]
        for file in files:
            id,file_id,file_name,file_info = file
            isGot = await asyncio.to_thread(is_got_file,user,id)
            if isGot:
                isGet[user_i] = True
                continue # переходим к следующему файлу
            try:
                await bot.send_document(
                    chat_id=user,
                    document=file_id,
                    caption=f"<b>{file_name}</b>\n\n<i>{file_info}</i>",
                    parse_mode='HTML'
                )
                isGet[user_i] = False
            # Отмечаем, что пользователь получил файл
                await asyncio.to_thread(got_file, user, id)
                await asyncio.sleep(5)
                break
            except Exception as e:
                await asyncio.to_thread(add_skip,user)
                print(f"❌Не удалось отправить файл {file_name} пользователю {user}: {e}\nДобавил бота в черный список")
                await bot.send_message(chat_id=config.admin,text=f"❌Не удалось отправить файл {file_name} пользователю {user}: {e}",
                                       parse_mode='HTML')
                break
        if isGet[user_i]:
            await bot.send_message(chat_id=config.admin,text=f"❗️Пользователь {user} получил уже все файлы \nВ этот раз ему ничего не отправили!")
        else:
            await bot.send_message(chat_id=config.admin,text=f"📬Пользователь {user} получил файл")
        user_i += 1
        if user_i == len(users):
            await bot.send_message(chat_id=config.admin,text="<i>💌Рассылка завершена</i>",
                                       parse_mode='HTML')
            return


#РАЗАДАЧА ФАЙЛА ПО ССЫЛКЕ
@dp.message(Command("start"))
async def get_file(message:types.Message):
    user_id = message.from_user.id
    await asyncio.to_thread(new_user,user_id,"okey")
    mes = message.text.split()
    if not len(mes) > 1:
        await message.answer("<i>👋Добро пожаловать!</i>",
                             parse_mode='HTML')
        return
    code = mes[1]
    if code.startswith("get_file_"):
        code = code.replace("get_file_","")
    data = await asyncio.to_thread(get_file_link,code)
    if not data["ok"]:
        await message.answer("❌ Файл не найден, обратитесь к отправителю ссылки")
        return
    file_id = data["data"][0]
    file_name = data["data"][1]
    file_info = data["data"][2]
    id_f = data["data"][3]
    if file_id:
        await asyncio.to_thread(got_file,user_id,id_f)
        await message.answer_document(document=file_id,
                                      caption=
f"""
<b>{file_name}</b>                               
<i>{file_info}</i>
""",
                                      parse_mode='HTML')
    

#/create - ВЫЗОВ КНОПОК ДЛЯ СОЗДАНИЯ
@dp.callback_query(F.data == "add_file")
async def stat(callback:CallbackQuery,state:FSMContext):
    id = callback.from_user.id
    await state.update_data(user_id = id)
    print(id)
    if not admin(config.admins, id):
        await callback.message.answer(
        "❌Нет прав на эту команду!"
    )
        await callback.answer()
        return
    await callback.message.answer("👀<i>Выбери что создать</i>",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_create)
    await callback.answer()
    

#/cencel - ОТМЕНА ВСЕХ ДЕЙСТВИЙ
@dp.callback_query(F.data == "cencel")
async def cencel(callback:CallbackQuery,state:FSMContext):
    await state.clear()
    await callback.message.answer("❗️Все действия <b>отменены</b> \n/admin<i> - админ панель (функции бота)</i>",
                                  parse_mode='HTML')
    await callback.answer()


#ОБРАБОТКА НОВЫХ ФАЙЛОВ
@dp.callback_query(F.data == "file")
async def craete_file(callback:CallbackQuery,state: FSMContext):
    await callback.message.edit_text("📁<b>СОЗДАЕМ ФАЙЛ</b>",
                                     parse_mode='HTML',
                                     reply_markup=None)
    await state.set_state(states.stateW.waiting_file)
    sent = await callback.message.answer(
        "📁Отправь файл <i>(не удаляй его в тг, иначе он пропадет из системе)</i>",
        parse_mode='HTML',
        reply_markup=keyboards.kb_cencel
    )
    await state.update_data(message_id=sent.message_id)
    await callback.answer()
@dp.message(states.stateW.waiting_file)
async def new_file(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    isCodeCheck = True
    while isCodeCheck:
        code = secrets.token_hex(4)
        isCodeCheck = await asyncio.to_thread(isCode,code)
    link = f"https://t.me/{config.bot_name}?start=get_file_{code}"
    await state.update_data(file_id = file_id,
                            code=code,
                            link=link)
    await state.set_state(states.stateW.waiting_name_file)
    await message.answer(
        "📩Введи <b>имя</b> для файла",
        parse_mode='HTML',
        reply_markup=keyboards.kb_cencel
    )
@dp.message(states.stateW.waiting_name_file)
async def nameFile(message: types.Message, state: FSMContext):
    name_file = message.text
    await state.update_data(name_file=name_file)
    await state.set_state(states.stateW.waiting_info_file)
    await message.answer(
        "📩Введи <b>описание</b> для файла, которое будет читать пользователь",
        parse_mode='HTML',
        reply_markup=keyboards.kb_cencel
    )
@dp.message(states.stateW.waiting_info_file)
async def infoFile(message: types.Message, state: FSMContext):
    info_file = message.text
    await state.update_data(info_file=info_file)
    data = await state.get_data()
    check = await asyncio.to_thread(input_file,
                                    data['file_id'],
                                    data['name_file'],
                                    data['info_file'],
                                    data['user_id'],
                                    data['code'])
    if not check:
        await message.answer("📛<b>Ошибка в сохранении</b>, файл НЕ добавлен в базу даных",
                             parse_mode='HTML')
        await state.clear()
        return
    await message.answer(f"""
♻️Файл <b>успешно сохранен</b> в базу данных <i>[files]</i>
                         
<b>Ссылка:</b> {data['link']}

🔗 <b>Tg_id</b>  файла: {data['file_id']}
📌 <b>Имя</b>  файла: {data['name_file']}
ℹ️ <b>Иформация</b>  о файле: {data['info_file']}
🆔 <b>Tg_id</b>  создателя: {data['user_id']}
📅 <b>Дата</b> создания: {datetime.now()}

<i>Можно продолжить создавать</i>""",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_create)
    await state.clear()
    

#КНОПКА ССЫЛКИ
@dp.callback_query(F.data == "link")
async def new_link(callback:CallbackQuery,state:FSMContext):
    await callback.message.edit_text("🔗<b>СОЗДАЕМ ССЫЛКУ</b>",
                                     parse_mode='HTML',
                                     reply_markup=None)                         
    await state.set_state(states.stateW.waiting_link)
    await callback.message.answer("🔗<i>Отправь ссылку</i>",
                                  parse_mode='HTML',
                                  reply_markup=keyboards.kb_cencel)
    await callback.answer()
@dp.message(states.stateW.waiting_link)
async def link(message: types.Message, state: FSMContext):
    link = message.text
    link_ww = await trueLink(link)
    ok = link_ww["ok"]
    error = link_ww["error"]
    if not ok:
        await message.answer(error)
        state.clear()
        return
    await state.set_state(states.stateW.waiting_label_link)
    await state.update_data(link=link)
    await message.answer("✏️Введи <b>подпись для кнопки</b> у ссылки",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
@dp.message(states.stateW.waiting_label_link)
async def label_link(message: types.Message, state: FSMContext):
    await state.update_data(label=message.text)
    await state.set_state(states.stateW.waiting_name_link)
    await message.answer("✏️Введи <b>имя</b> для ссылки",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
@dp.message(states.stateW.waiting_name_link)
async def name_link(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(states.stateW.waiting_info_link)
    await message.answer("✏️Введи информацию, которую будет видеть пользователь",
                         parse_mode='HTML',
                         reply_markup=keyboards.kb_cencel)
@dp.message(states.stateW.waiting_info_link)
async def info_link(message: types.Message, state: FSMContext):
    await state.update_data(info=message.text)
    data = await state.get_data()
    link = data['link']
    link_label = data['label']
    link_name = data['name']
    link_info = data['info']
    user_id = data['user_id']
    isLink = await asyncio.to_thread(input_link,
                                     link,
                                     link_label,
                                     link_name,
                                     link_info,
                                     user_id)
    if not isLink:
        await message.answer("📛<b>Ошибка в сохранении</b>, ссылка НЕ добавлена в базу даных",
                             parse_mode='HTML')
        await state.clear()
        return
    await message.answer(f"""
🔗Ссылка <b>успешно сохранена</b> в базу данных <i>[links]</i>
<b>Адрес</b>  ссылки: {data['link']}

<b>Подпись кнопки</b>  ссылки: {data['label']}
<b>Имя</b>  ссылки: {data['name']}
<b>Иформация</b> о ссылке: {data['info']}
<b>Tg_id</b>  создателя: {data['user_id']}
<b>Дата</b> создания: {datetime.now()}

<i>Можно продолжить создавать</i>""",
parse_mode='HTML',
reply_markup=keyboards.kb_create)
    await state.clear()


@dp.message(Command("info"))
async def info(message:types.Message):
    await message.answer(f"""
<i>Владелец: @egor47777</i>      

... ИНФОРМАЦИЯ О БОТЕ И ПРОЧЕЕ ...                         

<i>bot created by <a href="https://t.me/code_misty">misty</a></i>
""",
parse_mode='HTML',
disable_web_page_preview=True)#чтобы ссылка не сплывала



async def main():
    apscheduler.add_job(
        message_to_tgc,
        CronTrigger(hour=19,minute=00),
        id="tgc_message"
    )
    apscheduler.add_job(
        daily_massage,
        CronTrigger(hour=19,minute=00),
        id="dailyId"
    )
    apscheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())