from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0272(RuleTemplate):
    """
    CHK0272: An observational study (including patient registries) must be specified using the ObservationalStudyDesign class.

    Applies to: ObservationalStudyDesign
    Attributes: studyType
    """

    def __init__(self):
        super().__init__(
            "CHK0272",
            RuleTemplate.ERROR,
            "An observational study (including patient registries) must be specified using the ObservationalStudyDesign class.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
