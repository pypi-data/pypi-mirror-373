from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00151(RuleTemplate):
    """
    DDF00151: If geographic scope type is global then there must be only one geographic scope specified.

    Applies to: GovernanceDate
    Attributes: geographicScopes
    """

    def __init__(self):
        super().__init__(
            "DDF00151",
            RuleTemplate.ERROR,
            "If geographic scope type is global then there must be only one geographic scope specified.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
