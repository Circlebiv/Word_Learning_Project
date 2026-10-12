import logging
import sys

from PyQt6.QtWidgets import QApplication

from UI.UI_Connection.reg.login import Login

logging.basicConfig(
    level=logging.DEBUG,  # Переключатель: DEBUG (покажет всё), INFO (только важное)
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Указывает выводить логи в консоль
    ],
)

def main():
    app = QApplication([])
    login_window = Login()
    login_window.show()
    app.exec()



if __name__ == "__main__":
    main()