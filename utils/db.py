from firebase import Firebase


class Database(Firebase):
    def __init__(self, config):
        self.config = config

        super().__init__(self.config,)

        self._ = self.database()

    def get(self, key):
        return self._.child(key).get().val()

    def update(self, data):
        self._.child().update(data)
