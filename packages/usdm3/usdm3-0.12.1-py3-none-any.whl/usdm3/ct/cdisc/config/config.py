import os
import yaml


class Config:
    def __init__(self, filepath: str, filename: str = "ct_config.yaml"):
        self.filename = filename
        self.filepath = filepath
        f = open(os.path.join(self._full_filepath()))
        self._cdisc_ct_config = yaml.load(f, Loader=yaml.FullLoader)
        self._by_klass_attribute = {}
        self._process()

    def required_code_lists(self) -> list:
        return self._cdisc_ct_config["code_lists"]

    def required_packages(self) -> list:
        return self._cdisc_ct_config["packages"]

    def klass_and_attribute(self, klass, attribute) -> str:
        try:
            klass = klass if isinstance(klass, str) else klass.__name__
            return self._by_klass_attribute[klass][attribute]
        except Exception:
            raise ValueError(
                f"failed to find codelist for class '{klass}' attribute '{attribute}'"
            )

    def _process(self):
        for klass, info in self._cdisc_ct_config["klass_attribute_mapping"].items():
            if klass not in self._by_klass_attribute:
                self._by_klass_attribute[klass] = {}
            for attribute, cl in info.items():
                if attribute not in self._by_klass_attribute[klass]:
                    self._by_klass_attribute[klass][attribute] = cl

    def _full_filepath(self) -> str:
        return os.path.join(self.filepath, self.filename)
