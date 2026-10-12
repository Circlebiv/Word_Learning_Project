import logging
import sqlite3
import sys
from pathlib import Path



base_dir = Path(__file__).resolve().parent.parent

DB_PATH = base_dir / "Databases" / "russian_dictionary.db"
USERS_DB_PATH = base_dir / "Databases" / "users.db"

def add_user_word(word, trans, table):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("")