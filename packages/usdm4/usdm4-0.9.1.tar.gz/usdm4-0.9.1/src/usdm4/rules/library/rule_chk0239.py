from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0239(RuleTemplate):
    """
    CHK0239: Each study enrollment must apply to either a geographic scope, a study site, or a study cohort.

    Applies to: SubjectEnrollment
    Attributes: appliesTo
    """

    def __init__(self):
        super().__init__(
            "CHK0239",
            RuleTemplate.ERROR,
            "Each study enrollment must apply to either a geographic scope, a study site, or a study cohort.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
