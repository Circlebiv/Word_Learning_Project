from Core.word_operations import get_nickname


class UserSession:
    def __init__(self):
        self.current_user_id = None
        self.login = None
        self.current_user_nickname = None


    def log_in(self, user_id, login, nickname=None):
        self.current_user_id = user_id
        self.login = login
        if nickname:
            self.current_user_nickname = nickname
        else:
            self.current_user_nickname = get_nickname(login)

    def log_out(self):
        self.current_user_id = None
        self.login = None

    def is_authenticated(self):
        return self.current_user_id is not None

    def get_user_id(self):
        return self.current_user_id

    def get_login(self):
        return self.login

    def get_user_nickname(self):
        return self.current_user_nickname

state = UserSession()