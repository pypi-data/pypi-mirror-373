


class ConfigComponent: 


    # def __init__(self, *, name: str):
    #     self.name = name

    def to_json(self):
        response = {}

        # add attributes
        for key, value in self.__dict__.items():
            if value is None:
                continue

            if isinstance(value, ConfigComponent):
                response[key] = value.to_json()
            elif isinstance(value, list):
                response[key] = [v.to_json() if isinstance(v, ConfigComponent) else v for v in value]
            elif value is not None:
                response[key] = value

        return response