class Text:
    def __init__(self, text: str, value: any, x: float, y: float, text_col: tuple = (255,255,255)):
        self.text = text
        self.pos = (x,y)
        self.text_col = text_col
        self.value = value

    def get_data(self):
        return self.text, self.pos, self.text_col, self.value

    def set_value(self, v: any):
        self.value = v

    def get_value(self):
        return self.value

    def __str__(self):
        if self.value is not None:
            return f'{self.text}: {self.value}'
        else:
            return self.text