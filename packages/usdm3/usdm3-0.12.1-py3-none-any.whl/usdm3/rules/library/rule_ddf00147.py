from .rule_template import RuleTemplate


class RuleDDF00147(RuleTemplate):
    """
    DDF00147: An objective level must be specified using the objective level (C188725) DDF codelist.

    Applies to: Objective
    Attributes: level
    """

    def __init__(self):
        super().__init__(
            "DDF00147",
            RuleTemplate.ERROR,
            "An objective level must be specified using the objective level (C188725) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "Objective", "level")
