from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0202(RuleTemplate):
    """
    CHK0202: If a dose is specified then a corresponding frequency must also be specified.

    Applies to: Administration
    Attributes: dose
    """

    def __init__(self):
        super().__init__(
            "CHK0202",
            RuleTemplate.ERROR,
            "If a dose is specified then a corresponding frequency must also be specified.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
