from .rule_template import RuleTemplate


class RuleDDF00014(RuleTemplate):
    """
    DDF00014: A biomedical concept category is expected to have at least a member or a child.

    Applies to: BiomedicalConceptCategory
    Attributes: members, children
    """

    def __init__(self):
        super().__init__(
            "DDF00014",
            RuleTemplate.WARNING,
            "A biomedical concept category is expected to have at least a member or a child.",
        )
