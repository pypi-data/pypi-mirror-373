from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0264(RuleTemplate):
    """
    CHK0264: Within a study design, if more sub types are defined, they must be distinct.

    Applies to: InterventionalStudyDesign, ObservationalStudyDesign
    Attributes: subTypes
    """

    def __init__(self):
        super().__init__(
            "CHK0264",
            RuleTemplate.ERROR,
            "Within a study design, if more sub types are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
