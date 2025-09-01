from .rule_template import RuleTemplate


class RuleDDF00058(RuleTemplate):
    """
    DDF00058: Within an indication, if more indication codes are defined, they must be distinct.

    Applies to: Indication
    Attributes: codes
    """

    def __init__(self):
        super().__init__(
            "DDF00058",
            RuleTemplate.ERROR,
            "Within an indication, if more indication codes are defined, they must be distinct.",
        )
