import sys
from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QDialog

from Config.logger_config import log
from Core.identification import register_user
from Core.session import state
from UI.UI_Connection.reg.title_window import Title


class SignUp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UI_Design/register.ui', self)  # Загружаем дизайн
        self.sign_up_button.clicked.connect(self.sign_up)
        self.title_window = Title()

    def sign_up(self):
        login_text = self.login.text()
        conf_text = self.confirm_password.text()
        pass_text = self.password.text()

        if pass_text == conf_text:
            success, result = register_user(login_text, conf_text)  # дописать ошибку вывода
            self.close()
            self.title_window.show()

            if success:
                state.log_in(user_id=result, login=login_text)
                self.close()
                self.title_window.show()

            else:
                log.error(f"Unsuccessful attempt {result}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SignUp()
    ex.show()
    sys.exit(app.exec())
