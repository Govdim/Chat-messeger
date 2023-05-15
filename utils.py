from pywebio import session


def get_session_id() -> str:
    user_agent = session.info.user_agent
    os = user_agent.os
    browser = user_agent.browser

    return session.info.user_ip + "-" + os.family + "-" + os.version_string + "-" + browser.family + "-" + browser.version_string


def validate_auth(data: dict, info: dict):
    login = info["login"]
    password = info["password"]

    if login not in data:
        return "login", "Неверный логин!"
    if password != data[login]["password"]:
        return "password", "Неверный пароль!"


def validate_register(data: dict, info: dict):
    login = info["login"]
    password = info["password"]
    r_password = info["r_password"]

    if not login:
        return "login", "Обязательное поле!"
    if login in data:
        return "login", "Логин занят!"

    if not password:
        return "password", "Обязательное поле!"
    if password != r_password:
        return "r_password", "Пароли не совпадают!"


def validate_chat(data: dict):
    if data["command"] == "Отправить" and not data["message"]:
        return "message", "Введите текст сообщения!"
