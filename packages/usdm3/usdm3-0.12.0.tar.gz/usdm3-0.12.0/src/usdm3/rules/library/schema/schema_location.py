from simple_error_log import ErrorLocation


class SchemaErrorLocation(ErrorLocation):
    def __init__(self, path: str, instance):
        self.path = path
        self.instance = instance

    def to_dict(self):
        return {"path": self.path, "instance": self.instance}

    def __str__(self):
        return f"[{self.path}, {self.instance}]"
