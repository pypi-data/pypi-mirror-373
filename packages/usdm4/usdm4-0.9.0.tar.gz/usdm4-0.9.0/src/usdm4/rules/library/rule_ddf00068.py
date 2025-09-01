from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00068(RuleTemplate):
    """
    DDF00068: Each StudyArm must have one StudyCell for each StudyEpoch.

    Applies to: StudyCell
    Attributes: arm, epoch
    """

    def __init__(self):
        super().__init__(
            "DDF00068",
            RuleTemplate.ERROR,
            "Each StudyArm must have one StudyCell for each StudyEpoch.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
