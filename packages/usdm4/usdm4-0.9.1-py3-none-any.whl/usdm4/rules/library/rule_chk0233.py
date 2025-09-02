from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0233(RuleTemplate):
    """
    CHK0233: Every study role must apply to either a study version or at least one study design, but not both.

    Applies to: StudyRole
    Attributes: appliesTo
    """

    def __init__(self):
        super().__init__(
            "CHK0233",
            RuleTemplate.ERROR,
            "Every study role must apply to either a study version or at least one study design, but not both.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
