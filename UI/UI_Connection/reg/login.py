import sys

import keyring
from PyQt6 import uic
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QDialog

from Core.identification import login_user
from Core.session import state
from UI.UI_Connection.reg.register import SignUp
from UI.UI_Connection.title_window import Title

from Config.logger_config import log


class Login(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UI_Design/login.ui', self)  # Загружаем дизайн
        self.no_acc_button.clicked.connect(self.to_register)
        self.login_button.clicked.connect(self.to_login)
        self.is_remember_me_log.isChecked()
        self.sign_up_window = SignUp()


    def to_login(self):
        login_text = self.login_input.text()
        pass_text = self.password.text()
        # print(login, password)
        success, user_id = login_user(login_text, pass_text)

        if success:
            log.info(f"Successful attempt")
            state.log_in(user_id=user_id, login=login_text)
            if self.is_remember_me_log.isChecked():
                settings = QSettings("MyCompany", "MyApp")
                settings.setValue("login/last_username", login_text)
                settings.setValue("login/user_id", user_id)
                settings.setValue("login/remember_me", True)
                keyring.set_password("MyApp", str(user_id), pass_text)

            title_window = Title()
            title_window.show()
            self.close()

        # login_text = self.login.text()
        # login_user(login_text, self.pass_text)
        else:
            log.error(f"Unsuccessful attempt {user_id}")

    def to_register(self):
        self.sign_up_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login()
    ex.show()
    sys.exit(app.exec())
