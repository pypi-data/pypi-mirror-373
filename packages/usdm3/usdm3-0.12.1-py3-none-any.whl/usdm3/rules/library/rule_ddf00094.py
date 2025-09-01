from .rule_template import RuleTemplate


class RuleDDF00094(RuleTemplate):
    """
    DDF00094: Within a study version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.

    Applies to: StudyVersion
    Attributes: dateValues
    """

    def __init__(self):
        super().__init__(
            "DDF00094",
            RuleTemplate.WARNING,
            "Within a study version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.",
        )
