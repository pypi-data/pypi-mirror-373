from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00042(RuleTemplate):
    """
    DDF00042: The range specified for a planned age is not expected to be approximate.

    Applies to: Range
    Attributes: isApproximate
    """

    def __init__(self):
        super().__init__(
            "DDF00042",
            RuleTemplate.ERROR,
            "The range specified for a planned age is not expected to be approximate.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
