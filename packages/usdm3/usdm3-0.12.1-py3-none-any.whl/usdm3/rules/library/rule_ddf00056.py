from .rule_template import RuleTemplate


class RuleDDF00056(RuleTemplate):
    """
    DDF00056: Within a study design, if more therapeutic areas are defined, they must be distinct.

    Applies to: StudyDesign
    Attributes: therapeuticAreas
    """

    def __init__(self):
        super().__init__(
            "DDF00056",
            RuleTemplate.ERROR,
            "Within a study design, if more therapeutic areas are defined, they must be distinct.",
        )
