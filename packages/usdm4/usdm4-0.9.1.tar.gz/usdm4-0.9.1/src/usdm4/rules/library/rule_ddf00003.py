from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00003(RuleTemplate):
    """
    DDF00003: If the duration of an administration will vary, a quantity is not expected for the administration duration and vice versa.

    Applies to: AdministrationDuration
    Attributes: quantity
    """

    def __init__(self):
        super().__init__(
            "DDF00003",
            RuleTemplate.ERROR,
            "If the duration of an administration will vary, a quantity is not expected for the administration duration and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
