from .rule_template import RuleTemplate


class RuleDDF00075(RuleTemplate):
    """
    DDF00075: An activity is expected to refer to at least one procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.

    Applies to: Activity
    Attributes: definedProcedures, biomedicalConcepts, bcCategories, bcSurrogates
    """

    def __init__(self):
        super().__init__(
            "DDF00075",
            RuleTemplate.WARNING,
            "An activity is expected to refer to at least one procedure, biomedical concept, biomedical concept category or biomedical concept surrogate.",
        )
