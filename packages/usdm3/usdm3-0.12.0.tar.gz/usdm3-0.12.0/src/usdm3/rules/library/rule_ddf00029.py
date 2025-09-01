from .rule_template import RuleTemplate


class RuleDDF00029(RuleTemplate):
    """
    DDF00029: An encounter must only reference encounters that are specified within the same study design.

    Applies to: Encounter
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00029",
            RuleTemplate.ERROR,
            "An encounter must only reference encounters that are specified within the same study design.",
        )
