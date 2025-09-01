from simple_error_log.errors import Errors
from simple_error_log.error import Error
from usdm3.rules.library.rule_template import ValidationLocation


class RulesValidationResults:
    def __init__(self):
        self._items = {}

    def add_success(self, rule: str):
        self._items[rule] = {
            "status": "Success",
            "errors": None,
            "exception": None,
        }

    def add_failure(self, rule: str, errors: Errors):
        self._items[rule] = {
            "status": "Failure",
            "errors": [],
            "exception": None,
        }
        for error in errors._items:
            item = error.to_dict()
            self._items[rule]["errors"].append(item)

    def add_exception(self, rule: str, exception: Exception, traceback: str = ""):
        text = f"{str(exception)}\n\n{traceback}" if traceback else f"{str(exception)}"
        self._items[rule] = {
            "status": "Exception",
            "errors": None,
            "exception": text,
        }

    def add_not_implemented(self, rule: str):
        self._items[rule] = {
            "status": "Not Implemented",
            "errors": None,
            "exception": None,
        }

    def count(self):
        return len(self._items)

    def passed(self):
        return all(item["status"] == "Success" for item in self._items.values())

    def passed_or_not_implemented(self):
        return all(
            item["status"] == "Success" or item["status"] == "Not Implemented"
            for item in self._items.values()
        )

    def to_dict(self) -> list[dict]:
        if len(self._items) == 0:
            return []
        else:
            rows = []
            location = ValidationLocation(
                rule="", rule_text="", klass="", attribute="", path=""
            )
            for rule, item in self._items.items():
                if item["errors"]:
                    for error in item["errors"]:
                        row = {
                            "rule_id": rule,
                            "status": item["status"],
                            "exception": item["exception"],
                        }
                        row.update(self._flatten_error(error))
                        rows.append(row)
                else:
                    row = {
                        "rule_id": rule,
                        "status": item["status"],
                        "exception": item["exception"],
                    }
                    error = Error("", location, rule)
                    row.update(self._flatten_error(error.to_dict()))
                    rows.append(row)
            rows.sort(key=lambda x: x["rule_id"])
            return rows

    def _flatten_error(self, error: dict) -> dict:
        for key in ValidationLocation.headers():
            error[key] = ""
        for key, value in error["location"].items():
            if key in ValidationLocation.headers():
                error[key] = value
        error.pop("location")
        return error
