from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00086(RuleTemplate):
    """
    DDF00086: Syntax template text is expected to be HTML formatted.

    Applies to: EligibilityCriterion, Characteristic, Condition, Objective, Endpoint
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "DDF00086",
            RuleTemplate.ERROR,
            "Syntax template text is expected to be HTML formatted.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
