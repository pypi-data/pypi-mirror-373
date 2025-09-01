from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0238(RuleTemplate):
    """
    CHK0238: At least one attribute must be specified for an address.

    Applies to: Address
    Attributes: All
    """

    def __init__(self):
        super().__init__(
            "CHK0238",
            RuleTemplate.ERROR,
            "At least one attribute must be specified for an address.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
