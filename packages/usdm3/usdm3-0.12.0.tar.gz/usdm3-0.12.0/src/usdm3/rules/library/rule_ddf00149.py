from .rule_template import RuleTemplate


class RuleDDF00149(RuleTemplate):
    """
    DDF00149: A study arm data origin type must be specified according to the extensible data origin type (C188727) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyArm
    Attributes: dataOriginType
    """

    def __init__(self):
        super().__init__(
            "DDF00149",
            RuleTemplate.ERROR,
            "A study arm data origin type must be specified according to the extensible data origin type (C188727) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "StudyArm", "dataOriginType")
