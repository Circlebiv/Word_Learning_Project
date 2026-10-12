import sqlite3

# Подключение к базе данных (создание файла, если он не существует)
conn = sqlite3.connect('../../Databases/users.db')
cursor = conn.cursor()

# Создание таблицы users
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  login TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  registration_date DATE DEFAULT CURRENT_DATE)''')

# Создание таблицы learned_words
cursor.execute('''CREATE TABLE IF NOT EXISTS learned_words
                 (user_id INTEGER NOT NULL,
                  word TEXT NOT NULL,
                  progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

# Создание таблицы app_settings
cursor.execute('''CREATE TABLE IF NOT EXISTS app_settings
                 (user_id INTEGER NOT NULL,
                  setting_name TEXT NOT NULL UNIQUE,
                  setting_value TEXT NOT NULL,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

conn.commit()
conn.close()
