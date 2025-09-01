from .rule_template import RuleTemplate


class RuleDDF00089(RuleTemplate):
    """
    DDF00089: Any parameter name referenced in a tag in the text should be specified in the data dictionary parameter maps.

    Applies to: EligibilityCriterion, Characteristic, Condition, Objective, Endpoint
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "DDF00089",
            RuleTemplate.ERROR,
            "Any parameter name referenced in a tag in the text should be specified in the data dictionary parameter maps.",
        )
