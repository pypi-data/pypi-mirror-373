from .rule_template import RuleTemplate


class RuleDDF00134(RuleTemplate):
    """
    DDF00134: Within a study design, if more characteristics are defined, they must be distinct.

    Applies to: StudyDesign
    Attributes: characteristics
    """

    def __init__(self):
        super().__init__(
            "DDF00134",
            RuleTemplate.ERROR,
            "Within a study design, if more characteristics are defined, they must be distinct.",
        )
