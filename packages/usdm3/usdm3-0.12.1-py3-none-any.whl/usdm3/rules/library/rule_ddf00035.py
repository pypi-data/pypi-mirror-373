from .rule_template import RuleTemplate


class RuleDDF00035(RuleTemplate):
    """
    DDF00035: Within a code system and corresponding version, a one-to-one relationship between code and decode is expected.

    Applies to: Code
    Attributes: code, decode
    """

    def __init__(self):
        super().__init__(
            "DDF00035",
            RuleTemplate.WARNING,
            "Within a code system and corresponding version, a one-to-one relationship between code and decode is expected.",
        )
