import os
import yaml


class FileCache:
    def __init__(self, filepath: str, filename: str):
        self.filename = filename
        self.filepath = filepath

    def exists(self) -> bool:
        return self._file_exists()

    def save(self, data: dict) -> None:
        try:
            if not self._file_exists():
                with open(self._full_filepath(), "w") as f:
                    yaml.dump(data, f, indent=2, sort_keys=True)
        except Exception as e:
            raise Exception(f"Failed to save file '{self._full_filepath()}', {str(e)}")

    def read(self) -> dict:
        try:
            if self._file_exists():
                with open(self._full_filepath()) as f:
                    return yaml.safe_load(f)
            else:
                raise Exception(
                    f"Failed to read file '{self._full_filepath()}', does not exist"
                )
        except Exception as e:
            raise Exception(f"Failed to read file '{self._full_filepath()}', {str(e)}")

    def delete(self) -> None:
        try:
            os.remove(self._full_filepath())
        except Exception:
            pass

    def _file_exists(self) -> bool:
        return os.path.isfile(self._full_filepath())

    def _full_filepath(self) -> str:
        return os.path.join(self.filepath, self.filename)
