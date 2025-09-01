from .rule_template import RuleTemplate


class RuleDDF00074(RuleTemplate):
    """
    DDF00074: If the intervention model indicates a single group design then only one intervention is expected. In all other cases more interventions are expected.

    Applies to: StudyDesign
    Attributes: studyInterventions
    """

    def __init__(self):
        super().__init__(
            "DDF00074",
            RuleTemplate.WARNING,
            "If the intervention model indicates a single group design then only one intervention is expected. In all other cases more interventions are expected.",
        )
