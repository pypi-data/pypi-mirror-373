from .rule_template import RuleTemplate


class RuleDDF00079(RuleTemplate):
    """
    DDF00079: If a synonym is specified then it is not expected to be equal to the name of the biomedical concept (case insensitive).

    Applies to: BiomedicalConcept
    Attributes: synonyms
    """

    def __init__(self):
        super().__init__(
            "DDF00079",
            RuleTemplate.WARNING,
            "If a synonym is specified then it is not expected to be equal to the name of the biomedical concept (case insensitive).",
        )
