from .rule_template import RuleTemplate


class RuleDDF00124(RuleTemplate):
    """
    DDF00124: Referenced items in a parameter map must be available elsewhere in the data model.

    Applies to: ParameterMap
    Attributes: reference
    """

    def __init__(self):
        super().__init__(
            "DDF00124",
            RuleTemplate.ERROR,
            "Referenced items in a parameter map must be available elsewhere in the data model.",
        )
