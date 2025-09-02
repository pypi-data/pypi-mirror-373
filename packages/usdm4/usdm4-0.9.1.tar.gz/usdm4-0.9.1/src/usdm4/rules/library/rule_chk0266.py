from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0266(RuleTemplate):
    """
    CHK0266: Within a study design, if more intent types are defined, they must be distinct.

    Applies to: InterventionalStudyDesign
    Attributes: intentTypes
    """

    def __init__(self):
        super().__init__(
            "CHK0266",
            RuleTemplate.ERROR,
            "Within a study design, if more intent types are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
