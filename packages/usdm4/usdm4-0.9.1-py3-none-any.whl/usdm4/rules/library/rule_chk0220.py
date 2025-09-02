from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0220(RuleTemplate):
    """
    CHK0220: If a dose is specified, then a corresponding administrable product must also be specified either directly or embedded in the medical device and vice versa.

    Applies to: Administration
    Attributes: dose, administrableProduct
    """

    def __init__(self):
        super().__init__(
            "CHK0220",
            RuleTemplate.ERROR,
            "If a dose is specified, then a corresponding administrable product must also be specified either directly or embedded in the medical device and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
