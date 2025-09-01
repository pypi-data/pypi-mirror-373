from .rule_template import RuleTemplate


class RuleDDF00102(RuleTemplate):
    """
    DDF00102: A scheduled activity instance must only reference a timeline exit that is defined within the same schedule timeline as the scheduled activity instance.

    Applies to: ScheduledActivityInstance
    Attributes: timelineExit
    """

    def __init__(self):
        super().__init__(
            "DDF00102",
            RuleTemplate.ERROR,
            "A scheduled activity instance must only reference a timeline exit that is defined within the same schedule timeline as the scheduled activity instance.",
        )
