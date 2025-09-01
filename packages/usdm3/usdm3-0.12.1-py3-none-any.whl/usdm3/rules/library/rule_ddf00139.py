from .rule_template import RuleTemplate


class RuleDDF00139(RuleTemplate):
    """
    DDF00139: An identified organization is not expected to have more than one identifier for the study.

    Applies to: StudyIdentifier
    Attributes: studyIdentifierScope
    """

    def __init__(self):
        super().__init__(
            "DDF00139",
            RuleTemplate.WARNING,
            "An identified organization is not expected to have more than one identifier for the study.",
        )
