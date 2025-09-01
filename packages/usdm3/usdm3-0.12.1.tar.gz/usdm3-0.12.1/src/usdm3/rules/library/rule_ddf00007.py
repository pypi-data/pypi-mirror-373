from .rule_template import RuleTemplate


class RuleDDF00007(RuleTemplate):
    """
    DDF00007: If timing type is \"Fixed Reference\" then it must point to only one scheduled instance (e.g. attribute relativeToScheduledInstance must be equal to relativeFromScheduledInstance or it must be missing).

    Applies to: Timing
    Attributes: relativeToScheduledInstance
    """

    def __init__(self):
        super().__init__(
            "DDF00007",
            RuleTemplate.ERROR,
            'If timing type is "Fixed Reference" then it must point to only one scheduled instance (e.g. attribute relativeToScheduledInstance must be equal to relativeFromScheduledInstance or it must be missing).',
        )
