from json import loads, dumps


class Serializable:
    def to_json(self) -> str:
        return dumps(self.__dict__, default=lambda o: o.__dict__)

    def __str__(self) -> str:
        return str(self.to_json())

    @staticmethod
    def from_json_str(json_str: str):
        return loads(json_str)
