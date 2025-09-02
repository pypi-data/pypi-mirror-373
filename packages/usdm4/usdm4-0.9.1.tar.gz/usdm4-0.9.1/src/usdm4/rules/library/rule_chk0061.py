from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0061(RuleTemplate):
    """
    CHK0061: Each specified biomedical concept category is expected to be referenced by an activity.

    Applies to: Activity
    Attributes: bcCategories
    """

    def __init__(self):
        super().__init__(
            "CHK0061",
            RuleTemplate.ERROR,
            "Each specified biomedical concept category is expected to be referenced by an activity.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
