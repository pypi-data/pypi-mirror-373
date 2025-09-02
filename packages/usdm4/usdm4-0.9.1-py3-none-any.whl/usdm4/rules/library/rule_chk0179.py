from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0179(RuleTemplate):
    """
    CHK0179: The ordering of activities (using the previous and next attributes) must include the parents (e.g. activities refering to children) preceding their children.

    Applies to: Activity
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "CHK0179",
            RuleTemplate.ERROR,
            "The ordering of activities (using the previous and next attributes) must include the parents (e.g. activities refering to children) preceding their children. ",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
