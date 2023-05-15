import asyncio
import sqlite3

from pywebio import start_server, config
from pywebio.input import *
from pywebio.output import *
from sqlite3 import Connection

from settings import *
from utils import *

db: Connection
online_users = {}
user_data = {}

chat_messages = []


async def index():
    session.go_app("auth", new_window=False)


async def auth():
    put_row([
        put_text("Нет аккаунта?"),
        put_button("Регистрация", onclick=lambda: session.go_app("register", new_window=False))
    ], "120px")
    user_info = await input_group("Авторизация", [
        input("Логин", name="login"),
        input("Пароль", name="password", type=PASSWORD)
    ], validate=lambda info: validate_auth(user_data, info))

    online_users[get_session_id()] = user_info["login"]
    session.go_app("chat", new_window=False)


async def register():
    put_row([
        put_text("Уже есть аккаунт?"),
        put_button("Авторизация", onclick=lambda: session.go_app("auth", new_window=False))
    ], "150px")
    user_info = await input_group("Регистрация", [
        input("Логин", name="login"),
        select("Группа", ["МКИС21", "МКИС22", "МКИС23", "МКИС24", "МКИС25"], name="group"),
        input("Пароль", name="password", type=PASSWORD),
        input("Повторить пароль", name="r_password", type=PASSWORD)
    ], validate=lambda info: validate_register(user_data, info))

    db.cursor().execute("INSERT INTO users('login', 'group', 'password') VALUES('" + user_info["login"] + "', '" + user_info["group"] + "', '" + user_info["password"] + "')")
    db.commit()

    online_users[get_session_id()] = user_info["login"]
    user_data[user_info["login"]] = user_info
    session.go_app("chat", new_window=False)


async def chat():
    if get_session_id() not in online_users:
        session.go_app("auth", new_window=False)

    login = online_users[get_session_id()]
    group = user_data[login]["group"]
    put_markdown("📢 Добро пожаловать в онлайн чат МКИС!")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)
    refresh_task = session.run_async(refresh_messages(login, msg_box))

    for message in chat_messages:
        msg_box.append(put_markdown(message[1]))

    while True:
        data = await input_group("💭 Новое сообщение", [
            input(placeholder="Текст сообщения ...", name="message"),
            actions(name="command", buttons=["Отправить", {'label': "Выйти из аккаунта", 'type': 'cancel', 'color': 'danger'}])
        ], validate=lambda m: validate_chat(m))

        if data is None:
            break

        message = f"`[{group}] {login}`: {data['message']}"
        msg_box.append(put_markdown(message))
        chat_messages.append((login, message))

    refresh_task.close()
    online_users.pop(get_session_id())
    session.go_app("auth", new_window=False)


async def refresh_messages(login, msg_box):
    global chat_messages
    last_index = len(chat_messages)

    while True:
        await asyncio.sleep(0.5)

        for message in chat_messages[last_index:]:
            if message[0] != login:
                msg_box.append(put_markdown(message[1]))

        if len(chat_messages) > MAX_MESSAGES:
            chat_messages = chat_messages[len(chat_messages) // 2:]

        last_index = len(chat_messages)


if __name__ == "__main__":
    db = sqlite3.connect("users.db")
    result = db.cursor().execute("SELECT * FROM users").fetchall()
    for user in result:
        user_data[user[1]] = {"group": user[2], "password": user[3]}

    config(title=APPLICATION_TITLE, theme=APPLICATION_THEME)
    start_server([index, auth, register, chat], port=SERVER_PORT, debug=True, cdn=False)
