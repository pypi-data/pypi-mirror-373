from .rule_template import RuleTemplate


class RuleDDF00088(RuleTemplate):
    """
    DDF00088: Epoch ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.

    Applies to: StudyEpoch
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00088",
            RuleTemplate.WARNING,
            "Epoch ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.",
        )
