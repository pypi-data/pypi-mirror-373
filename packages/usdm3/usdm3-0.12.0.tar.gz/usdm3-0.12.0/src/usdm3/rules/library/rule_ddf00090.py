from .rule_template import RuleTemplate


class RuleDDF00090(RuleTemplate):
    """
    DDF00090: The same Biomedical Concept Category must not be referenced more than once from the same activity.

    Applies to: Activity
    Attributes: bcCategories
    """

    def __init__(self):
        super().__init__(
            "DDF00090",
            RuleTemplate.ERROR,
            "The same Biomedical Concept Category must not be referenced more than once from the same activity.",
        )
