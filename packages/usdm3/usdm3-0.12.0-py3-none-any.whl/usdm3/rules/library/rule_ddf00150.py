from .rule_template import RuleTemplate


class RuleDDF00150(RuleTemplate):
    """
    DDF00150: An encounter type must be specified according to the extensible encounter type (C188728) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Encounter
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "DDF00150",
            RuleTemplate.ERROR,
            "An encounter type must be specified according to the extensible encounter type (C188728) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "Encounter", "type")
