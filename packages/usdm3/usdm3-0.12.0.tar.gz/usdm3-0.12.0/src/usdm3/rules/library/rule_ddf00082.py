import os
import pathlib
from usdm3.rules.library.rule_template import RuleTemplate
from usdm3.rules.library.schema.schema_location import SchemaErrorLocation
from usdm3.rules.library.schema.schema_validation import (
    SchemaValidation,
    ValidationError,
)
from usdm3.data_store.data_store import DataStore


class RuleDDF00082(RuleTemplate):
    """
    DDF00082: Data types of attributes (string, number, boolean) must conform with the USDM schema based on the API specification.

    Applies to: All
    Attributes: All
    """

    def __init__(self):
        super().__init__(
            "DDF00082",
            RuleTemplate.ERROR,
            "Data types of attributes (string, number, boolean) must conform with the USDM schema based on the API specification.",
        )

    def validate(self, config: dict) -> bool:
        try:
            data: DataStore = config["data"]
            validator = SchemaValidation(self._schema_path())
            validator.validate_file(data.filename, "Wrapper-Input")
            return True
        except ValidationError as e:
            location = SchemaErrorLocation(e.json_path, e.instance)
            self._errors.add(f"Message: {e.message}\nContext: {e.context}", location)
            return False

    def _schema_path(self) -> str:
        root = pathlib.Path(__file__).parent.resolve()
        return os.path.join(root, "schema/usdm_v3.json")
