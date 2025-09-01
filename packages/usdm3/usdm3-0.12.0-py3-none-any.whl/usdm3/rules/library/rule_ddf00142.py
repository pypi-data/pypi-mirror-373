from .rule_template import RuleTemplate


class RuleDDF00142(RuleTemplate):
    """
    DDF00142: A governance date type must be specified according to the extensible governance date type (C207413) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: GovernanceDate
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "DDF00142",
            RuleTemplate.ERROR,
            "A governance date type must be specified according to the extensible governance date type (C207413) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "GovernanceDate", "type")
