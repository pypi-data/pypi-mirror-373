from .rule_template import RuleTemplate


class RuleDDF00065(RuleTemplate):
    """
    DDF00065: A scheduled decision instance is not expected to have a sub-timeline.

    Applies to: ScheduledDecisionInstance
    Attributes: timeline
    """

    def __init__(self):
        super().__init__(
            "DDF00065",
            RuleTemplate.WARNING,
            "A scheduled decision instance is not expected to have a sub-timeline.",
        )
