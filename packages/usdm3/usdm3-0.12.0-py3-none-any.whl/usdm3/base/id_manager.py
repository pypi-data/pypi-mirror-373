import re


class IdManager:
    def __init__(self, classes: list[str]):
        self._classes = classes
        self._id_index = {}
        self.clear()

    def clear(self):
        for klass in self._classes:
            name = klass if isinstance(klass, str) else klass.__name__
            self._id_index[name] = 0

    def build_id(self, klass):
        klass_name = klass if isinstance(klass, str) else str(klass.__name__)
        self._id_index[klass_name] += 1
        return f"{klass_name}_{self._id_index[klass_name]}"

    def add_id(self, klass_name: str, id: str) -> None:
        if instance := self._find_id_instance(id):
            if instance > self._id_index[klass_name]:
                self._id_index[klass_name] = instance

    def _find_id_instance(self, id_text: str) -> int | None:
        pattern = r"^.+_(\d+)$"
        match = re.match(pattern, id_text)
        return int(match.group(1)) if match else None
