from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00017(RuleTemplate):
    """
    DDF00017: Within subject enrollment, the quantity must be a number or a percentage (i.e. the unit must be empty or %).

    Applies to: SubjectEnrollment
    Attributes: quantity
    """

    def __init__(self):
        super().__init__(
            "DDF00017",
            RuleTemplate.ERROR,
            "Within subject enrollment, the quantity must be a number or a percentage (i.e. the unit must be empty or %).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
