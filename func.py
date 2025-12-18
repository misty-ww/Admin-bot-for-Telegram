import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import json


#ПОЛУЧИТЬ СООБЩЕНИЕ ДЛЯ РАССЫЛКИ В tgc
def get_1_mes_tgc():
    try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT id,text FROM message_tgc ORDER BY id ASC LIMIT 1")
            return cursor.fetchone()
    except Exception as e:
            print (e)
            return None
    finally:
            if cursor:
                cursor.close()
            if db:
                db.close()


#УДАЛИТЬ СОО ПО id ДЛЯ tgc
async def delete_mes_tgc(idM):
    try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("DELETE FROM message_tgc WHERE id = ?",(idM,))
            if cursor.rowcount == 1:
                return True
            return False
    except Exception as e:
            print (e)
            return False
    finally:
            db.commit()
            if cursor:
                cursor.close()
            if db:
                db.close()


#ПРОСМОТР ВСЕХ СООБЩЕНИЙ ДЛЯ РАССЫЛКИ
async def check_all_mess_tgc():
    try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT id,text,date FROM message_tgc")
            return cursor.fetchall()
    except Exception as e:
            print (e)
            return None
    finally:
            db.commit()
            if cursor:
                cursor.close()
            if db:
                db.close()

#ДОБАВЛЕНИЕ СОО ДЛЯ РАССЫЛКИ
async def input_mes_tgc(text):
    try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("INSERT INTO message_tgc (text) VALUES (?)",(text,))
            if cursor.rowcount == 1:
                return True
            return False
            
    except Exception as e:
            print (e)
            return False
    finally:
            db.commit()
            if cursor:
                cursor.close()
            if db:
                db.close()


#РАБОТА c JSON
async def get_Json(r_w:str,dan):
    try:
        if r_w == "r":
            with open("date.json","r",encoding="utf-8") as file:
                date = json.load(file)
            return date
        if r_w == "w":
            with open("date.json", "w",encoding="utf-8") as file:   
                json.dump(dan,file,ensure_ascii=False,indent=2)
            return "Load"  
    except:
        return None

#УДАЛЕНИЕ ФАЙЛА ИЗ РАССЫЛКИ
def delete_file(id):
    if id:
        try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM files WHERE id = ?",
                           (id,)
                           )
            if not cursor.fetchone():
                return False
            cursor.execute("DELETE FROM files WHERE id = ?",
                           (id,)
                            )
            db.commit()
            return True
        except Exception as e:
            return False
        finally:
            if cursor:
                cursor.close()
                db.close()
def delete_file_user(id):
    if id:
        try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM sent_user WHERE file_id = ?",
                           (id,)
                           )
            if not cursor.fetchone():
                return False
            cursor.execute("DELETE FROM sent_user WHERE file_id = ?",
                           (id,)
                            )
            db.commit()
            return True
        except Exception as e:
            return False
        finally:
            if cursor:
                cursor.close()
                db.close()
     

#ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ В ЧС
def add_skip(user_id):
    if user_id:
        try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("UPDATE users SET status = ? WHERE user_id = ?",("skip",user_id,))
            db.commit()
        finally:
            if cursor:
                cursor.close()
                db.close()
     

#ПРОВЕРКА ВЫДАВАЛСЯ ЛИ ФАЙЛ РАНЕЕ
def is_got_file(user_id,file_id):
        try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM sent_user WHERE user_id = ? AND file_id = ?",
                           (user_id,file_id))
            if cursor.fetchone():
                return True
            return False
            
        except Exception as e:
            print (e)
            return False
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()


#БЕРЕМ ФАЙЛЫ ДЛЯ РАЗДАЧИ
def get_id_files():
        try:
            db = sqlite3.connect("db.db")
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM files")
            files = cursor.fetchone()
            if not files:
                return None
            cursor.execute("SELECT id,file_id,file_name,file_info FROM files")
            files = cursor.fetchall()
            return files
        except Exception as e:
            print (e)
            return None
        finally:
            if cursor:
                cursor.close()
            if db:
                db.close()

#БЕРЕМ ПОЛЬЗОВАТЕЛЕЙ ДЛЯ РАЗДАЧИ
def get_users(status):
    try:
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM users")
        users = cursor.fetchone()
        if not users:
            return None
        cursor.execute("SELECT user_id FROM users WHERE status = ?",(status,))
        users = cursor.fetchall()
        return users
    except Exception as e:
            print (e)
            return None
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

#ВСТАВКА ПОЛУЧЕНЫХ ДОКОВ
def got_file(user_id,id):
    try:
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM sent_user WHERE user_id = ? AND file_id = ?",(user_id,id))
        row = cursor.fetchone()
        if row:
            return
        cursor.execute("INSERT INTO sent_user (user_id,file_id) VALUES(?,?)",(user_id,id))
        db.commit()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


#РЕГИСТР ПОЛЬЗОВАТЕЛЕЙ
def new_user(user_id,status):
    try:
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?",(user_id,))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET status = ? WHERE user_id = ?",("okey",user_id,))
            print("ПОЛЬЗОВАТЕЛЬ БЫЛ")
            db.commit()
            return
        cursor.execute("""
INSERT INTO users (user_id,status) VALUES (?,?) 
""",(user_id,status))
        if cursor.fetchall is not None:
            db.commit()
            print("НОВЫЙ ПОЛЬЗОВАТЕЛЬ ЗАПИСАН!!!")
        db.commit()
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    

#ВЫТАСКИВАЕМ ФАЙЛ ИЗ БД
def get_file_link(code):
    try:
        db = sqlite3.connect("db.db")
        cursor = db.cursor()
        cursor.execute("""
                       SELECT file_id, file_name, file_info,id
                       FROM files
                       WHERE code = ?
""",(code,))
        row = cursor.fetchone()
        if row:
            return {'ok':True,
                    'data':row}
        else:
            return {'ok':False,
                    'error':"файл не найден"}
    except Exception as e:
        print(f"Ошибка в get_file_link: {e}")
        return {
            "ok": False,
            "error": "Ошибка базы данных"
        }
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


#ПРОВЕРКА ССЫЛКИ
async def trueLink(link):
    if not link.startswith(('http://','https://')):
        return {"ok":False,"error":"❌ Некорректная ссылка"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(link,timeout=5) as resp:
                if resp.status != 200:
                    return {"ok":False,"error":f"❌ Ошибка {resp.status}"}
                content_type = resp.headers.get('Content-Type')
                return {"ok":True,"content_type":content_type,"error":"Ссылка доступна"}
    except:
        return {"ok":False,"error":"❌ Ссылка недоступна"}



#ПРОВЕРКА АДМИН ЛИ
def admin(admins, id):
    if id in admins:
        return True
    return False

#ПРОВЕРКА ЕСТЬ ЛИ ЭТОТ КОД
def isCode(code):
    try:
        db = sqlite3.connect('db.db')
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM files WHERE code=?", (code,))
        if cursor.fetchone() is not None:
            return True
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
#ВСТАВЛЯЕТ В БД LINKS
def input_link(link,link_label,link_name,link_info,user_id):
    try:
        db = sqlite3.connect('db.db')
        cursor = db.cursor()
        cursor.execute("""
INSERT INTO links (link,link_label,link_name,link_info,user_id) VALUES (?,?,?,?,?)
                            """ , (link,link_label,link_name,link_info,user_id))
        if cursor.fetchall() is not None:
            db.commit()
            return True
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


#ВСТАВЛЯЕТ В БД ФАЙЛЫ
def input_file(file_id,file_name,file_info,user_id,code):
    try:
        db = sqlite3.connect('db.db')
        cursor = db.cursor()
        cursor.execute("""
INSERT INTO files (file_id,file_name,file_info,user_id,code) VALUES (?,?,?,?,?)
                            """ , (file_id,file_name,file_info,user_id,code))
        if cursor.fetchall() is not None:
            db.commit()
            return True
        return False
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


#ВОЗРАЩАЕТ КНОПКУ С ССЫЛКОЙ И НАЗВАНИЕ КОТОРЫЕ ЗАДАЛИ
def link_kb(text,new_url):
    kb_link = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text=text,url=new_url)]
    ]
)
    return kb_link