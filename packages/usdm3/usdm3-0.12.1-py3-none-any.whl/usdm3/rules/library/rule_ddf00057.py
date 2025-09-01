from .rule_template import RuleTemplate


class RuleDDF00057(RuleTemplate):
    """
    DDF00057: Within a study design, if more trial intent types are defined, they must be distinct.

    Applies to: StudyDesign
    Attributes: trialIntentTypes
    """

    def __init__(self):
        super().__init__(
            "DDF00057",
            RuleTemplate.ERROR,
            "Within a study design, if more trial intent types are defined, they must be distinct.",
        )
