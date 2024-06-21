class MessageModel:
    status: str
    pin: int
    name: str

    def __init__(self, status, pin, name):
        self.status = status
        self.pin = pin
        self.name = name

    def to_dict(self):
        return {
            "status": self.status,
            "pin": self.pin,
            "name": self.name
        }
