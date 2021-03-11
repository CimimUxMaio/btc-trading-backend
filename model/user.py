from model.bot import Bot


class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.active_bots = []

    def register_bot(self, new_bot: Bot):
        new_bot.start()
        self.active_bots.append(new_bot)

    def get_bot_by_id(self, bot_id):
        return next((b for b in self.active_bots if b.id.int == bot_id), None)