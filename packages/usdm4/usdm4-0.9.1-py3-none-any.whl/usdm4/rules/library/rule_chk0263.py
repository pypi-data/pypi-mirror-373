from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0263(RuleTemplate):
    """
    CHK0263: Within a study design, if more characteristics are defined, they must be distinct.

    Applies to: InterventionalStudyDesign, ObservationalStudyDesign
    Attributes: characteristics
    """

    def __init__(self):
        super().__init__(
            "CHK0263",
            RuleTemplate.ERROR,
            "Within a study design, if more characteristics are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
