import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog

from Core.identification import login_user
from Core.session import state
from UI.UI_Connection.reg.register import SignUp
from UI.UI_Connection.reg.title_window import Title

from Config.logger_config import log



class Login(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UI_Design/login.ui', self)  # Загружаем дизайн
        self.no_acc_button.clicked.connect(self.to_register)
        self.login_button.clicked.connect(self.to_login)
        self.title_window = Title()
        self.sign_up_window = SignUp()

    def to_login(self):
        login = self.login_input.text()
        password = self.password.text()

        success, result = login_user(login, password)

        if success:
            state.log_in(user_id=result, login=login)
            self.close()
            self.title_window.show()
        # login_text = self.login.text()
        # login_user(login_text, self.pass_text)
        else:
            log.error(f"Unsuccessful attempt {result}")



    def to_register(self):
        self.close()
        self.sign_up_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login()
    ex.show()
    sys.exit(app.exec())
