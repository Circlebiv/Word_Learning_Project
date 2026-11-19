import sqlite3
from pathlib import Path

import bcrypt
import keyring
import mariadb
from PyQt6.QtCore import QSettings

from Config.logger_config import log
from Core.session import state

base_dir = Path(__file__).resolve().parent.parent

DB_PATH = base_dir / "Databases" / "russian_dictionary.db"
USERS_DB_PATH = base_dir / "Databases" / "users.db"

conn_params = {
    "host": 'localhost',
    "user": 'admin',
    "password": 'G2g3ZJYlDkrFSo',
    "database": "my_database"
}


def forget_user(user_id):
    settings = QSettings("MyCompany", "MyApp")
    is_remembered = settings.value("login/remember_me")
    saved_username = settings.value("login/last_username")
    saved_user_id = settings.value("login/user_id", type=int)


    if is_remembered and saved_username and saved_user_id == user_id:
        settings.setValue("login/remember_me", False)

        log.info("Has forgotten successfully")
    else:
        log.error("No such user")

def is_remember_me_active():
    settings = QSettings("MyCompany", "MyApp")
    is_remembered = settings.value("login/remember_me", False, type=bool)
    saved_username = settings.value("login/last_username")
    saved_user_id = settings.value("login/user_id")

    if is_remembered and saved_username and saved_user_id:

        saved_password = keyring.get_password("MyApp", saved_user_id)
        if saved_password:
            success, result = login_user(saved_username, saved_password)
            if success:
                state.log_in(user_id=result, login=saved_username)
                return True
    return False


def check_user(login):
    with mariadb.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
            return cursor.fetchone() is not None


def register_user(login, password, nickname):
    if not login or len(login) < 3:
        return False, "Login must be at least 3 symblos"
    if not password or len(password) < 3:
        return False, "Password must be at least 3 symblos"

    try:
        with mariadb.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                if check_user(login):
                    return False, "User with this login is already exist"

                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                cursor.execute(
                    "INSERT INTO users (login, nickname, password_hash) VALUES (?, ?, ?)",
                    (login, nickname, hashed_password.decode('utf-8'))
                )
                conn.commit()

                new_user_id = cursor.lastrowid

                return True, new_user_id

    except sqlite3.IntegrityError:
        log.warning(f"Attempt to register existing login: '{login}'")
        return False, "User with this login is already exist"
    except sqlite3.Error as e:
        log.error(f"Db Error '{login}': {e}", exc_info=True)
        return False, f"Db Error: {e}"


def login_user(login, password):
    try:
        with mariadb.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password_hash FROM users WHERE login = ?", (login,))
                user_data = cursor.fetchone()

                if user_data is None:
                    return False, "no_data"

                user_id, bd_pass = user_data

                # Password checking
                is_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    bd_pass.encode('utf-8')
                )

                if is_valid:
                    log.info("Checking passed")
                    return True, user_id

                else:
                    log.info("Wrong password")
                    return False, "Wrong answer"

    except mariadb.Error as e:
        log.error(f"Db Error: {e}")
        return False, "Error"


print(check_user("zabiv"))
