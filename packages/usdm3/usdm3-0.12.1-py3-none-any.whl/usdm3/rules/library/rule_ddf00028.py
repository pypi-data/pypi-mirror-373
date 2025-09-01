from .rule_template import RuleTemplate


class RuleDDF00028(RuleTemplate):
    """
    DDF00028: An activity must only reference activities that are specified within the same study design.

    Applies to: Activity
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00028",
            RuleTemplate.ERROR,
            "An activity must only reference activities that are specified within the same study design.",
        )
