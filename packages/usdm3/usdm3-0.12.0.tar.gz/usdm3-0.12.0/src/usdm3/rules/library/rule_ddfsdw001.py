from .rule_template import RuleTemplate
from usdm3.__info__ import __model_version__ as model_version


class RuleDDFSDW001(RuleTemplate):
    """
    DDFSDW001: The version in the wrapper should be set to 3.0.0
    Applies to: Wrapper
    Attributes: usdmVersion
    """

    def __init__(self):
        super().__init__(
            "DDFSDW001",
            RuleTemplate.ERROR,
            "The version in the wrapper should be set to 3.0.0",
        )

    def validate(self, config: dict) -> bool:
        return self._validate_version(config, model_version)

    def _validate_version(self, config: dict, version: str) -> bool:
        data = config["data"]
        items = data.instances_by_klass("Wrapper")
        if (
            len(items) == 1
            and "usdmVersion" in items[0]
            and items[0]["usdmVersion"] == version
        ):
            pass
        else:
            self._add_failure(
                f"Invalid version detected, not set to {version}",
                "Wrapper",
                "usdmVersion",
                data.path_by_id("$root"),
            )
        return self._result()
