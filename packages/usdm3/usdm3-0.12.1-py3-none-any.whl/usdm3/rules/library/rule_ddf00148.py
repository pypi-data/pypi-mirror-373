from .rule_template import RuleTemplate


class RuleDDF00148(RuleTemplate):
    """
    DDF00148: An endpoint level must be specified using the endpoint level (C188726) DDF codelist.

    Applies to: Endpoint
    Attributes: level
    """

    def __init__(self):
        super().__init__(
            "DDF00148",
            RuleTemplate.ERROR,
            "An endpoint level must be specified using the endpoint level (C188726) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "Endpoint", "level")
