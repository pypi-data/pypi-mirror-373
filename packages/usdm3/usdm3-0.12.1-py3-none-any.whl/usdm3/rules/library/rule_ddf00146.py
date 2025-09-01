from .rule_template import RuleTemplate


class RuleDDF00146(RuleTemplate):
    """
    DDF00146: A study title type must be specified using the study title type (C207419) DDF codelist.

    Applies to: StudyTitle
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "DDF00146",
            RuleTemplate.ERROR,
            "A study title type must be specified using the study title type (C207419) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "StudyTitle", "type")
