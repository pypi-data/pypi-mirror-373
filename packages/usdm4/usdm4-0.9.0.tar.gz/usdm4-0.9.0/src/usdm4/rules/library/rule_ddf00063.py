from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00063(RuleTemplate):
    """
    DDF00063: A standard code alias is not expected to be equal to the standard code (e.g. no equal code or decode for the same coding system version is expected).

    Applies to: AliasCode
    Attributes: standardCodeAliases
    """

    def __init__(self):
        super().__init__(
            "DDF00063",
            RuleTemplate.ERROR,
            "A standard code alias is not expected to be equal to the standard code (e.g. no equal code or decode for the same coding system version is expected).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
