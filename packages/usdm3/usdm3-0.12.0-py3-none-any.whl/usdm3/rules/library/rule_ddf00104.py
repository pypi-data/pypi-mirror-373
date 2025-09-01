from .rule_template import RuleTemplate


class RuleDDF00104(RuleTemplate):
    """
    DDF00104: A timing's relative to/from property must be specified using the Timing Relative To From Value Set Terminology (C201265) SDTM codelist.

    Applies to: Timing
    Attributes: relativeToFrom
    """

    def __init__(self):
        super().__init__(
            "DDF00104",
            RuleTemplate.ERROR,
            "A timing's relative to/from property must be specified using the Timing Relative To From Value Set Terminology (C201265) SDTM codelist.",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "Timing", "relativeToFrom")
