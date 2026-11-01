import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='admin',
        password='G2g3ZJYlDkrFSo'
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS my_database")

    cursor.execute("USE my_database")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            login VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            registration_date DATE DEFAULT (CURRENT_DATE)
        ) ENGINE=InnoDB
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned_words (
            user_id INT NOT NULL,
            word VARCHAR(255) NOT NULL,
            progress INT DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            user_id INT NOT NULL,
            setting_name VARCHAR(255) NOT NULL UNIQUE,
            setting_value TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB
    ''')

    conn.commit()
    print("Все таблицы успешно созданы в MariaDB!")

except Error as e:
    print(f"Ошибка: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
