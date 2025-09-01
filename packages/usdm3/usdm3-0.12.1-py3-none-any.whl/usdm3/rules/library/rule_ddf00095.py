from .rule_template import RuleTemplate


class RuleDDF00095(RuleTemplate):
    """
    DDF00095: Within a study protocol document version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.

    Applies to: StudyProtocolDocumentVersion
    Attributes: dateValues
    """

    def __init__(self):
        super().__init__(
            "DDF00095",
            RuleTemplate.WARNING,
            "Within a study protocol document version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.",
        )
