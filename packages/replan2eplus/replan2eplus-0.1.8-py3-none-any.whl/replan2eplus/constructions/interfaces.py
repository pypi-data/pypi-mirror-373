from dataclasses import dataclass


@dataclass
class ConstructionsObject:
    Name: str
    Outside_Layer: str
    Layer_2: str = ""
    Layer_3: str = ""
    Layer_4: str = ""
    Layer_5: str = ""
    Layer_6: str = ""

    @property
    def materials(self):
        possible = [
            self.Outside_Layer,
            self.Layer_2,
            self.Layer_3,
            self.Layer_4,
            self.Layer_5,
            self.Layer_6,
        ]
        return [i for i in possible if i]

    @property
    def valid_dict(self):
        res = {k: v for k, v in self.__dict__.items() if v}
        print(res)
        return res
