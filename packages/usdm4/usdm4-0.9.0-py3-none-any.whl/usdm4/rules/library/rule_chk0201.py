from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0201(RuleTemplate):
    """
    CHK0201: If an administration's dose is specified then a corresponding route is expected and vice versa.

    Applies to: Administration
    Attributes: dose, route
    """

    def __init__(self):
        super().__init__(
            "CHK0201",
            RuleTemplate.ERROR,
            "If an administration's dose is specified then a corresponding route is expected and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
