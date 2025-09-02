from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0174(RuleTemplate):
    """
    CHK0174: An eligility criterion must not be referenced by both a study design population and any of the cohorts of the same study design population.

    Applies to: StudyVersion
    Attributes: criteria
    """

    def __init__(self):
        super().__init__(
            "CHK0174",
            RuleTemplate.ERROR,
            "An eligility criterion must not be referenced by both a study design population and any of the cohorts of the same study design population.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
