from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0004(RuleTemplate):
    """
    CHK0004: Within a study design, there must be at least 1 eligibility criterion that is referenced by either a study population or a cohort.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: criteria
    """

    def __init__(self):
        super().__init__(
            "CHK0004",
            RuleTemplate.ERROR,
            "Within a study design, there must be at least 1 eligibility criterion that is referenced by either a study population or a cohort.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
