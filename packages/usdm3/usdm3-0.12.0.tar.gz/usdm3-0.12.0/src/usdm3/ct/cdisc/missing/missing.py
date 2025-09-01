import os
import yaml


class Missing:
    def __init__(self, file_path: str):
        f = open(os.path.join(file_path, "missing_ct.yaml"))
        self._missing_ct = yaml.load(f, Loader=yaml.FullLoader)

    def code_lists(self):
        for response in self._missing_ct:
            yield response
