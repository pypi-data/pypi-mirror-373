from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0219(RuleTemplate):
    """
    CHK0219: A referenced substance must not have any references itself.

    Applies to: Substance
    Attributes: referenceSubstance
    """

    def __init__(self):
        super().__init__(
            "CHK0219",
            RuleTemplate.ERROR,
            "A referenced substance must not have any references itself.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
