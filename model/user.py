from model.strategies.tradingstrategy import TradingStrategy
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

    def register_bot(self, strategy: TradingStrategy):
        new_bot = Bot(self, strategy)
        new_bot.start()
        self.__active_bots.append(new_bot)

    def unregister_bot(self, bot_id):
        self.__active_bots = list(filter(lambda bot: bot.id != bot_id, self.__active_bots))

    def get_bot_by_id(self, bot_id):
        return next((b for b in self.active_bots if b.id == bot_id), None)

    def next_bot_id(self):
        self.__bot_id_acum += 1
        return self.__bot_id_acum