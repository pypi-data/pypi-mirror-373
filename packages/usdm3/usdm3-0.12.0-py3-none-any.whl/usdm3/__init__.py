import pathlib
from usdm3.rules.rules_validation import RulesValidation3
from usdm3.rules.rules_validation_results import RulesValidationResults
from usdm3.minimum.minimum import Minimum
from usdm3.api.wrapper import Wrapper


class USDM3:
    def __init__(self):
        self.root = self._root_path()
        self.validator = RulesValidation3(self.root)

    def validate(self, file_path: str) -> RulesValidationResults:
        return self.validator.validate(file_path)

    def minimum(self, study_name: str, sponsor_id: str, version: str) -> Wrapper:
        return Minimum.minimum(self.root, study_name, sponsor_id, version)

    def _root_path(self) -> str:
        return pathlib.Path(__file__).parent.resolve()
