from PyQt6 import uic
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QHeaderView, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
from Core.search import search_in_dictionary
from Core.session import state, UserSession
from Core.word_operations import add_user_word, get_all_user_words
from Core.identification import forget_user

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

        self.is_phrasal.setChecked(False)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Word", "Translation", "Word progress", "Last review"])
        self.tree = self.treeView
        self.tree.setModel(self.model)

        self.to_fill_tree()
        # self.searchline.textChanged.connect(self.search_function)

        self.searched_words_table.setSortingEnabled(True)  # Sorting with click on heading

        self.forget_me_btn.clicked.connect(self.handle_forget_me)

    def handle_forget_me(self):
        log.info("Send to executor function")
        print(state.get_user_id())
        forget_user(state.get_user_id())

    def clear_tree(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Word", "Translation", "Word progress", "Last review"])

    def to_fill_tree(self):
        self.clear_tree()
        user_id = state.get_user_id()
        log.info(f"Got user_id: {user_id}")
        words = get_all_user_words(user_id)
        log.info(f"Got user's words: {words}")

        user_tables = {}
        for word in words:
            table = word.user_folder_name
            word_text = word.word

            if table not in user_tables:
                user_tables[table] = QStandardItem(table)
                self.model.appendRow(user_tables[table])

            parent_item = user_tables[table]
            child_text = QStandardItem(word_text)
            child_trans = QStandardItem(word.translation)
            child_progress = QStandardItem(str(word.progress))
            child_lr = QStandardItem(str(word.last_review))

            parent_item.appendRow([child_text, child_trans, child_progress, child_lr])
            # self.tree.collapseAll()

    #
    # def on_item_expanded(self, index):
    #     item = self.model.itemFromIndex(index)
    #     # plug
    #     if item.rowCount() == 1 and item.child(0).text() == "Loading...":
    #         item.removeRow(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.search_function()

    def search_function(self):
        text = self.searchline.text().strip()
        is_it_phrase = self.is_phrasal.isChecked()
        # print(f"----------{text} {self.selected_table}")

        found_words = search_in_dictionary(text, self.selected_table, is_it_phrase)
        self.searched_words_table.clear()
        self.searched_words_table.setRowCount(len(found_words))  # Bug fixed why -1 ?
        self.searched_words_table.setColumnCount(3)
        self.searched_words_table.setHorizontalHeaderLabels(
            ['Words', "Translation", "Action"])  # Add another langs

        for row, pair in enumerate(found_words):
            word, trans, group = pair

            self.searched_words_table.setItem(row, 0, QTableWidgetItem(str(word)))
            self.searched_words_table.setItem(row, 1, QTableWidgetItem(str(trans)))

            btn = QPushButton('Add')
            btn.clicked.connect(lambda checked, r=row: self.add_word_mlist(r, group))
            self.searched_words_table.setCellWidget(row, 2, btn)

            # Smart column width
            header = self.searched_words_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(True)

    def add_word_mlist(self, row, group_item):
        word_item = self.searched_words_table.item(row, 0).text()
        trans_item = self.searched_words_table.item(row, 1).text()

        if word_item and trans_item:

            user_id = state.get_user_id()
            log.info(f"Got user_id: {user_id}")

            # Delegate to core: add word to user's vocabulary
            add_user_word(word_item, trans_item, user_id, group_item)

            log.info(f"Added word: {word_item} из строки {row}")
            self.to_fill_tree()
        else:
            log.error(f"Word with number {row + 1} wasn't find")
