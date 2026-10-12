import logging
import re
import sqlite3
import sys
from pathlib import Path

from Config.logger_config import log



def search_in_dictionary(words, table):
    log.info(f"Получена строка для поиска: '{words}'")
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "Databases" / "russian_dictionary.db"

    ru = False
    en = False

    if re.match(r'^[a-zA-Z\s\-\']+$', ' '.join(words)):  # All en letters
        en = True

    if re.search(r'[а-яА-ЯёЁ]', ' '.join(words)):  # Only one ru letter
        ru = True

    if ru:
        wtf_search = ('bare', 'translations_en')
    else:
        wtf_search = ('translations_en', 'bare')

    if not db_path.exists():
        log.error(f"Файл базы данных не найден по пути: {db_path}")
        return list()

    words = words.replace(',', '').replace('.', '').split()
    con = sqlite3.connect(db_path)
    result = list()

    cur = con.cursor()
    for word in words:
        if table == 'All':
            searched = cur.execute(f"""SELECT * FROM (
                                        SELECT {wtf_search[0]}, {wtf_search[1]}, 'noun' AS source_table FROM nouns
                                        UNION ALL
                                        SELECT {wtf_search[0]}, {wtf_search[1]}, 'verb' AS source_table FROM verbs
                                        UNION ALL
                                        SELECT {wtf_search[0]}, {wtf_search[1]}, 'others' AS source_table FROM others
                                        UNION ALL
                                        SELECT {wtf_search[0]}, {wtf_search[1]}, 'adjectives' AS source_table FROM adjectives
                                        ) 
                                        WHERE {wtf_search[0]} LIKE '%{word}%'

                                                """).fetchall()
        else:
            searched = cur.execute(f"""SELECT {wtf_search[0]}, {wtf_search[1]}
                                        FROM {table}
                                        WHERE {wtf_search[0]} LIKE '%{word}%'
                                        """).fetchall()
        if searched:
            log.info(
                f"Для слова '{word}' найдено совпадений в БД: {len(searched)}"
            )
        else:
            log.warning(
                f"Для слова '{word}' ничего не найдено в базе данных."
            )

        result.append(searched)

    con.close()
    log.debug("Соединение с базой данных закрыто.")
    flattened = list()
    if ru:
        for word_and_translation in result:  # [('человек', 'person, people; man'), ... ]
            for meaning in word_and_translation:
                for elem in meaning[1].replace(";", ",").split(","):
                    flattened.append((meaning[0], elem, meaning[-1]))
    elif en:
        print(result)
        for word_and_translation in result:
            print(word_and_translation)
            for meaning in word_and_translation:
                print(meaning)
                for elem in meaning[0].replace(";", ",").split(","):
                    flattened.append((elem.strip(), meaning[1],  meaning[-1]))

    # Short (more appropriate) words become first
    # Added x[0] not in words to return imputed word firstly
    flattened = sorted(flattened, key=lambda x: (x[0] not in words, len(x[0])))

    log.info(f"Успешно обработано. Итоговый список (всего {len(flattened)}):")

    # for elem in flattened:
    #     logger.info(f"Выбрано: {elem}")

    return flattened

# print(search_in_dictionary('человек', 'All'))

# print(search_in_dictionary('man', 'All'))
