import sys

import keyring
from PyQt6 import uic
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QDialog

from Config.logger_config import log
from Core.identification import register_user
from Core.session import state
from UI.UI_Connection.title_window import Title


class SignUp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UI_Design/register.ui', self)  # Загружаем дизайн
        self.sign_up_button.clicked.connect(self.sign_up)
        self.title_window = Title()
        self.is_remember_me_reg.isChecked()

    def sign_up(self):
        login_text = self.login.text()
        conf_text = self.confirm_password.text()
        pass_text = self.password.text()
        nickname = self.nickname.text()


        if pass_text == conf_text:
            success, user_id = register_user(login_text, conf_text, nickname)  # Add error handlers


            if success:
                print("111")
                state.log_in(user_id=user_id, login=login_text)
                if self.is_remember_me_reg.isChecked():
                    settings = QSettings("MyCompany", "MyApp")
                    settings.setValue("login/last_username", login_text)
                    settings.setValue("login/user_id", user_id)
                    settings.setValue("login/remember_me", True)
                    keyring.set_password("MyApp", str(user_id), pass_text)

                self.close()
                self.title_window.show()

            else:
                log.error(f"Unsuccessful attempt {user_id}")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SignUp()
    ex.show()
    sys.exit(app.exec())
