from .rule_template import RuleTemplate


class RuleDDF00078(RuleTemplate):
    """
    DDF00078: If a transition start rule is defined then an end rule is expected and vice versa.

    Applies to: StudyElement, Encounter
    Attributes: transitionStartRule, transitionEndRule
    """

    def __init__(self):
        super().__init__(
            "DDF00078",
            RuleTemplate.WARNING,
            "If a transition start rule is defined then an end rule is expected and vice versa.",
        )
