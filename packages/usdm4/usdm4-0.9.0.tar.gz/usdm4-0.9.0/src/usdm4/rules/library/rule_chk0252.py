from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0252(RuleTemplate):
    """
    CHK0252: An administrable product sourcing must be specified using the sourcing (Cxxx) DDF codelist.

    Applies to: AdministrableProduct
    Attributes: sourcing
    """

    def __init__(self):
        super().__init__(
            "CHK0252",
            RuleTemplate.ERROR,
            "An administrable product sourcing must be specified using the sourcing (Cxxx) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
