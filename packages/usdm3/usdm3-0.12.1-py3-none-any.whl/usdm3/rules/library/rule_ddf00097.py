from .rule_template import RuleTemplate


class RuleDDF00097(RuleTemplate):
    """
    DDF00097: Within a study design, the planned age range must be specified either in the study population or in all cohorts.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: plannedAge
    """

    def __init__(self):
        super().__init__(
            "DDF00097",
            RuleTemplate.ERROR,
            "Within a study design, the planned age range must be specified either in the study population or in all cohorts.",
        )
