class gateway:
    id = "id"
    name = "name"

    def __init__(
        self, id, name
    ):
        self.id = id
        self.name = name

    @classmethod
    def from_dict(self, dictionary):
        id = dictionary.get(self.id)
        name = dictionary.get(self.name)

        return self(id, name)

    def __repr__(self):
        return f"{str(self.__dict__)}"
