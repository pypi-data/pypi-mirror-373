from .rule_template import RuleTemplate


class RuleDDF00100(RuleTemplate):
    """
    DDF00100: Within a study version, there must be no more than one title of each type.

    Applies to: StudyVersion
    Attributes: titles
    """

    def __init__(self):
        super().__init__(
            "DDF00100",
            RuleTemplate.ERROR,
            "Within a study version, there must be no more than one title of each type.",
        )
