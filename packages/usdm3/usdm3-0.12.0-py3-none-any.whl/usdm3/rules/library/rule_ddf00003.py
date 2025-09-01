from .rule_template import RuleTemplate


class RuleDDF00003(RuleTemplate):
    """
    DDF00003: If the duration of an administration will vary, a quantity is not expected for the administration duration and vice versa.

    Applies to: AdministrationDuration
    Attributes: quantity
    """

    def __init__(self):
        super().__init__(
            "DDF00003",
            RuleTemplate.WARNING,
            "If the duration of an administration will vary, a quantity is not expected for the administration duration and vice versa.",
        )
