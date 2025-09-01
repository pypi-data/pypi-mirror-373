import json
from simple_error_log.errors import Errors
from simple_error_log import ErrorLocation


class DataStoreErrorLocation(ErrorLocation):
    def __init__(self, path: str, klass: str, attribute: str):
        self.path = path
        self.klass = klass
        self.attribute = attribute

    def to_dict(self):
        return {"path": self.path, "klass": self.klass, "attribute": self.attribute}

    def __str__(self):
        return f"[{self.klass}', '{self.attribute}' @ '{self.path}']"


class DecompositionError(Exception):
    def __init__(self, error: DataStoreErrorLocation, message: str):
        self.error = error
        self.message = message

    def __str__(self):
        return f"error decomposing the '.json' file, {self.message}, at {self.error}"


class DataStore:
    def __init__(self, filename: str):
        self._klasses = {}
        self._ids = {}
        self._parent = {}
        self._path = {}
        self.filename = filename
        self.data = None
        self.errors = Errors()

    def decompose(self):
        self.data = self._load_data()
        self._check_study_id(self.data)
        self._decompose(self.data, None, "")

    def instance_by_id(self, id: str) -> dict:
        if id not in self._ids:
            return None
        return self._ids[id]

    def path_by_id(self, id: str) -> str:
        if id not in self._path:
            return None
        return self._path[id]

    def instances_by_klass(self, klass: str) -> list:
        if klass not in self._klasses:
            return []
        return list(self._klasses[klass].values())

    def parent_by_klass(self, id: str, klasses: str | list) -> dict:
        klasses = [klasses] if isinstance(klasses, str) else klasses
        found = False
        if id not in self._ids:
            return None
        instance = self._ids[id]
        while not found:
            if "instanceType" not in instance:
                return None
            elif instance["instanceType"] in klasses:
                found = True
            else:
                instance = self._parent[instance["id"]]
        return instance

    def _decompose(self, data, parent, path, instance_index=None) -> None:
        if isinstance(data, dict):
            path = self._add_klass_instance(data, parent, path, instance_index)
            for key, value in data.items():
                if isinstance(value, dict):
                    self._decompose(value, data, path)
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        self._decompose(item, data, path, index)

    def _add_klass_instance(self, data, parent, path, instance_index) -> None:
        id, klass = self._check_id_klass(parent, data, path)
        path = self._update_path(path, data, instance_index)
        if klass not in self._klasses:
            self._klasses[klass] = {}
        if id in self._ids:
            location = DataStoreErrorLocation(path, klass, "id")
            self.errors.add("Duplicate id '{id}' detected", location, "DUP_ID")
        self._klasses[klass][id] = data
        self._ids[id] = data
        self._path[id] = path
        self._parent[id] = parent
        return path

    def _load_data(self) -> dict:
        with open(self.filename, "r") as file:
            return json.load(file)

    def _update_path(self, path: str, data: dict, instance_index: int) -> str:
        path = path + "." + data["instanceType"] if "instanceType" in data else "$"
        path = path + f"[{instance_index}]" if instance_index is not None else path
        return path

    def _check_id_klass(self, parent: dict, data: dict, path: str) -> None:
        id, error = self._check_id(parent, data, path)
        if error:
            raise DecompositionError(error, "missing id attribute")
        klass, error = self._check_instance_type(parent, data, path)
        if error:
            raise DecompositionError(error, "missing instanceType attribute")
        return id, klass

    def _check_id(self, parent: dict, data: dict, path: str) -> None:
        if parent:
            if "id" in data:
                return data["id"], None
            else:
                klass = data["instanceType"] if "instanceType" in data else ""
                return None, DataStoreErrorLocation(path, klass, "id")
        else:
            return "$root", None

    def _check_instance_type(self, parent: dict, data: dict, path: str) -> None:
        if parent:
            if "instanceType" in data:
                return data["instanceType"], None
            else:
                id = data["id"] if "id" in data else ""
                return None, DataStoreErrorLocation(
                    path, f"missing instanceType for id '{id}'", "instanceType"
                )
        else:
            return "Wrapper", None

    def _check_study_id(self, data):
        # Do not want a null study id though it is permitted
        if "study" not in data:
            location = DataStoreErrorLocation("$", "study", "")
            raise DecompositionError(location, "missing study attribute")
        if "id" not in data["study"]:
            location = DataStoreErrorLocation("$.Study", "study", "id")
            raise DecompositionError(location, "missing id attribute")
        data["study"]["id"] = (
            "$root.study.id" if data["study"]["id"] is None else data["study"]["id"]
        )
