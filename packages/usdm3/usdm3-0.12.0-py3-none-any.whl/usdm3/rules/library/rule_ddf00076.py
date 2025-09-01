from .rule_template import RuleTemplate


class RuleDDF00076(RuleTemplate):
    """
    DDF00076: If a biomedical concept is referenced from an activity then it is not expected to be referenced as well by a biomedical concept category that is referenced from the same activity.

    Applies to: Activity, BiomedicalConceptCategory
    Attributes: biomedicalConcepts, members
    """

    def __init__(self):
        super().__init__(
            "DDF00076",
            RuleTemplate.WARNING,
            "If a biomedical concept is referenced from an activity then it is not expected to be referenced as well by a biomedical concept category that is referenced from the same activity.",
        )
