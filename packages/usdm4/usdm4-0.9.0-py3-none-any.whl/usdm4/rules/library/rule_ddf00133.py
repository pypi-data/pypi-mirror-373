from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00133(RuleTemplate):
    """
    DDF00133: Within a study design, if a planned enrollment number is defined, it must be specified either in the study population or in all cohorts.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: plannedEnrollmentNumber
    """

    def __init__(self):
        super().__init__(
            "DDF00133",
            RuleTemplate.ERROR,
            "Within a study design, if a planned enrollment number is defined, it must be specified either in the study population or in all cohorts.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
