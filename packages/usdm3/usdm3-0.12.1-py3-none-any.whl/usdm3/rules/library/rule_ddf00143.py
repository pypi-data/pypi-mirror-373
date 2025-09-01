from .rule_template import RuleTemplate


class RuleDDF00143(RuleTemplate):
    """
    DDF00143: A study amendment reason must be coded using the study amendment reason (C207415) DDF codelist.

    Applies to: StudyAmendmentReason
    Attributes: code
    """

    def __init__(self):
        super().__init__(
            "DDF00143",
            RuleTemplate.ERROR,
            "A study amendment reason must be coded using the study amendment reason (C207415) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "StudyAmendmentReason", "code")
