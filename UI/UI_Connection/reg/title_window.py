import logging
import sys
from PyQt6 import uic, QtGui  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QHeaderView, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
from Core.search import search_in_dictionary
from  Core.user_service import add_user_word

from Config.logger_config import log


class Title(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UI_Design/title1.ui', self)
        self.search_switcher.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.main_switcher.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.options_switcher.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.search_button.clicked.connect(self.search_function)

        self.selected_table = self.table_chooser.currentText()

        # self.searchline.textChanged.connect(self.search_function)

        self.searched_words_table.setSortingEnabled(True)  # Сортировка кликом по заголовку

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.search_function()

    def search_function(self):
        text = self.searchline.text().strip()

        print(f"----------{text} {self.selected_table}")

        found_words = search_in_dictionary(text, self.selected_table)
        self.searched_words_table.clear()
        self.searched_words_table.setRowCount(len(found_words) - 1)
        self.searched_words_table.setColumnCount(3)
        self.searched_words_table.setHorizontalHeaderLabels(
            ['Words', "Translation", "Action"])  # Добавить изменение языка интерфейса

        for row, pair in enumerate(found_words):
            word, trans, table = pair

            self.searched_words_table.setItem(row, 0, QTableWidgetItem(str(word)))
            self.searched_words_table.setItem(row, 1, QTableWidgetItem(str(trans)))

            btn = QPushButton('Добавить')
            btn.clicked.connect(lambda checked, r=row: self.add_word_mlist(r))
            self.searched_words_table.setCellWidget(row, 2, btn)

            # Умная ширина колонок
            header = self.searched_words_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(True)

    def add_word_mlist(self, row):
        word_item = self.searched_words_table.item(row, 0)
        trans_item = self.searched_words_table.item(row, 1)
        table_item = self.searched_words_table.item(row, 2)

        if word_item and trans_item:
            word = word_item.text()
            # Delegate to core: add word to user's vocabulary
            add_user_word(word_item, trans_item, table_item)

            log.info(f"Добавляем слово: {word} из строки {row}")
        else:
            log.error(f"Слово под номером {row + 1} не найдено")
