import sqlite3
from pathlib import Path

import bcrypt

from Config.logger_config import log

base_dir = Path(__file__).resolve().parent.parent

DB_PATH = base_dir / "Databases" / "russian_dictionary.db"
USERS_DB_PATH = base_dir / "Databases" / "users.db"




def get_connection():
    return sqlite3.connect(USERS_DB_PATH)


def check_user(login):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        return cursor.fetchone() is not None


def register_user(login, password):
    if not login or len(login) < 3:
        return False, "Login must be at least 3 symblos"
    if not password or len(password) < 3:
        return False, "Password must be at least 3 symblos"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            if check_user(login):
                return False, "User with this login is already exist"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute(
                "INSERT INTO users (login, password_hash) VALUES (?, ?)",
                (login, hashed_password.decode('utf-8'))
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
        with get_connection() as conn:
            cursor = conn.cursor()

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

    except sqlite3.Error as e:
        log.error(f"Db Error: {e}")
        return False, "Error"
