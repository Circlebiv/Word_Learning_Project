import logging
import sys

from PyQt6.QtWidgets import QApplication

from Core.identification import is_remember_me_active
from UI.UI_Connection.reg.login import Login
from UI.UI_Connection.title_window import Title
from Config.logger_config import log


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
)

def main():
    app = QApplication([])
    if is_remember_me_active():
        log.info("User recognized. Skipping Login")
        window = Title()
    else:
        log.info("No user recognized. Opening Login")
        window = Login()


    window.show()
    app.exec()



if __name__ == "__main__":
    main()