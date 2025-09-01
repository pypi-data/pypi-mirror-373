from .rule_template import RuleTemplate


class RuleDDF00010(RuleTemplate):
    """
    DDF00010: The names of all child instances of the same parent class must be unique.

    Applies to: All
    Attributes: name
    """

    def __init__(self):
        super().__init__(
            "DDF00010",
            RuleTemplate.ERROR,
            "The names of all child instances of the same parent class must be unique.",
        )
