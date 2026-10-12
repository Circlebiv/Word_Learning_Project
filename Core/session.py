
class UserSession:
    def __init__(self):
        self.current_user_id = None
        self.login = None

    def log_in(self, user_id, login):
        self.current_user_id = user_id
        self.login = login

    def log_out(self):
        self.current_user_id = None
        self.login = None

    def is_authenticated(self):
        return self.current_user_id is not None

state = UserSession()