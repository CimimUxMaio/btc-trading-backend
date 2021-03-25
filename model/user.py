from model.bot import Bot


class User:
    def __init__(self, email, password_hash):
        self.__email = email
        self.__password_hash = password_hash
        self.__active_bots = []
        self.__bot_id_acum = 0

    @property
    def email(self):
        return self.__email

    @property
    def password_hash(self):
        return self.__password_hash

    @property
    def active_bots(self):
        return self.__active_bots

    def register_bot(self, strategy, name=None):
        id = self.__next_bot_id()
        final_name = name if name is not None else str(id)
        self.__active_bots.append(Bot(id=id, name=final_name, strategy=strategy))

    def unregister_bot(self, bot_id):
        self.__active_bots = list(filter(lambda bot: bot.id != bot_id, self.__active_bots))

    def get_bot_by_id(self, bot_id):
        return next((bot for bot in self.active_bots if bot.id == bot_id), None)

    def __next_bot_id(self):
        self.__bot_id_acum += 1
        return self.__bot_id_acum
