from .rule_template import RuleTemplate


class RuleDDF00005(RuleTemplate):
    """
    DDF00005: Every study version must have exactly one study identifier with an identifier scope that references a clinical study sponsor organization.

    Applies to: StudyIdentifier
    Attributes: studyIdentifierScope
    """

    def __init__(self):
        super().__init__(
            "DDF00005",
            RuleTemplate.ERROR,
            "Every study version must have exactly one study identifier with an identifier scope that references a clinical study sponsor organization.",
        )
