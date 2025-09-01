from .rule_template import RuleTemplate


class RuleDDF00085(RuleTemplate):
    """
    DDF00085: Narrative content text is expected to be HTML formatted.

    Applies to: NarrativeContent
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "DDF00085",
            RuleTemplate.WARNING,
            "Narrative content text is expected to be HTML formatted.",
        )
