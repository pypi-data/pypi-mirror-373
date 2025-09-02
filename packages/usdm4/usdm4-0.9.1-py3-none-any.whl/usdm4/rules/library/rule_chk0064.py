from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0064(RuleTemplate):
    """
    CHK0064: Each specified biomedical concept surrogate is expected to be referenced by an activity.

    Applies to: Activity
    Attributes: bcSurrogates
    """

    def __init__(self):
        super().__init__(
            "CHK0064",
            RuleTemplate.ERROR,
            "Each specified biomedical concept surrogate is expected to be referenced by an activity.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
