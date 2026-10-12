import csv
import sqlite3
import os


def detect_delimiter(sample_line: str) -> str:
    """
    Определяет разделитель CSV, поддерживая , ; и \\t (табуляция).
    Выбирает тот символ, который встречается чаще всего в строке-образце.
    """
    candidates = {',': sample_line.count(','),
                  ';': sample_line.count(';'),
                  '\t': sample_line.count('\t')}
    best = max(candidates, key=candidates.get)
    if candidates[best] == 0:
        raise ValueError("Не удалось определить разделитель — проверьте файл вручную")
    return best


def create_sqlite_from_csv(db_name="russian_dictionary.db",
                            csv_folder="Databases/russian-dictionary-master"):
    # Делаем путь абсолютным относительно расположения САМОГО скрипта,
    # а не текущей рабочей директории (которая зависит от того, откуда запущено).
    if not os.path.isabs(csv_folder):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_folder = os.path.join(script_dir, csv_folder)

    if not os.path.isdir(csv_folder):
        raise FileNotFoundError(
            f"Папка с CSV не найдена: {csv_folder}\n"
            f"Проверьте путь csv_folder или передайте абсолютный путь явно."
        )

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    tables_config = {
        'adjectives': 'adjectives.csv',
        'nouns': 'nouns.csv',
        'verbs': 'verbs.csv',
        'others': 'others.csv',
    }

    # Поля, по которым обязательно нужен индекс, если они есть в таблице
    searchable_fields = ('bare', 'accented', 'translations_en', 'translations_de')

    for table_name, filename in tables_config.items():
        filepath = os.path.join(csv_folder, filename)

        if not os.path.exists(filepath):
            print(f"Файл {filepath} не найден, пропускаем")
            continue

        print(f"Обрабатываем {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.readline()
            f.seek(0)
            delimiter = detect_delimiter(sample)
            print(f"  Разделитель определён как: {delimiter!r}")

            reader = csv.DictReader(f, delimiter=delimiter)
            columns = reader.fieldnames

            if not columns or len(columns) < 2:
                print(f"  ВНИМАНИЕ: похоже, разделитель определён неверно "
                      f"({len(columns) if columns else 0} колонок). Пропускаем.")
                continue

            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
            create_sql = f'''
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {', '.join(f'"{col}" TEXT' for col in columns)}
                )
            '''
            cursor.execute(create_sql)

            placeholders = ', '.join('?' for _ in columns)
            col_names = ', '.join(f'"{col}"' for col in columns)
            insert_sql = f'INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})'

            rows = [[row.get(col, '').strip() for col in columns] for row in reader]

            if rows:
                cursor.executemany(insert_sql, rows)
                print(f"  Добавлено {len(rows)} записей, колонок: {len(columns)}")

            # Индексы только по тем полям, что реально есть в этой таблице
            for field in searchable_fields:
                if field in columns:
                    cursor.execute(
                        f'CREATE INDEX IF NOT EXISTS idx_{table_name}_{field} '
                        f'ON {table_name}("{field}")'
                    )

        conn.commit()

    # Сводная таблица для поиска по всем частям речи сразу.
    # ВАЖНО: используем только общие для всех таблиц колонки, иначе UNION ALL упадёт
    # из-за разного числа/порядка столбцов в adjectives/nouns/verbs/others.
    common_cols = ['bare', 'accented', 'translations_en', 'translations_de']

    cursor.execute('DROP TABLE IF EXISTS dictionary')
    select_parts = []
    for pos, table in [('adjective', 'adjectives'), ('noun', 'nouns'),
                        ('verb', 'verbs'), ('other', 'others')]:
        cursor.execute(f"PRAGMA table_info({table})")
        table_cols = [row[1] for row in cursor.fetchall()]
        if not table_cols:
            continue
        select_cols = ', '.join(
            f'"{c}"' if c in table_cols else 'NULL' for c in common_cols
        )
        select_parts.append(
            f"SELECT id AS source_id, '{pos}' AS part_of_speech, {select_cols} FROM {table}"
        )

    if not select_parts:
        conn.commit()
        conn.close()
        raise RuntimeError(
            "Ни одна исходная таблица (adjectives/nouns/verbs/others) не была создана — "
            "проверьте, что CSV-файлы найдены и правильно распарсены (см. сообщения выше)."
        )

    # ВАЖНО: id в adjectives/nouns/verbs/others начинается заново с 1 в каждой таблице,
    # поэтому просто скопировать его в dictionary НЕЛЬЗЯ — id перестанет быть уникальным
    # (одному и тому же id будут соответствовать 4 разных слова из разных таблиц).
    # source_id сохраняем отдельно для справки/отладки, а настоящим первичным ключом
    # dictionary делаем свежий ROW_NUMBER() — он гарантированно уникален по всей таблице
    # и годится как content_rowid для FTS5 ниже.
    cursor.execute(f'''
        CREATE TABLE dictionary AS
        SELECT ROW_NUMBER() OVER () AS id, source_id, part_of_speech,
               bare, accented, translations_en, translations_de
        FROM ({" UNION ALL ".join(select_parts)})
    ''')
    cursor.execute('CREATE UNIQUE INDEX idx_dictionary_id ON dictionary(id)')
    cursor.execute('CREATE INDEX idx_dictionary_bare ON dictionary(bare)')
    cursor.execute('CREATE INDEX idx_dictionary_translations_en ON dictionary(translations_en)')

    # Полнотекстовый поиск (быстрый поиск по слову/переводу, с опечатками через MATCH)
    cursor.execute('DROP TABLE IF EXISTS dictionary_fts')
    cursor.execute('''
        CREATE VIRTUAL TABLE dictionary_fts USING fts5(
            bare, accented, translations_en, translations_de,
            content='dictionary', content_rowid='id'
        )
    ''')
    cursor.execute('''
        INSERT INTO dictionary_fts(rowid, bare, accented, translations_en, translations_de)
        SELECT id, bare, accented, translations_en, translations_de FROM dictionary
    ''')

    conn.commit()
    conn.close()
    print(f"\nБаза данных успешно создана: {db_name}")


if __name__ == "__main__":
    create_sqlite_from_csv()