from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00096(RuleTemplate):
    """
    DDF00096: All primary endpoints must be referenced by a primary objective.

    Applies to: Endpoint
    Attributes: level
    """

    def __init__(self):
        super().__init__(
            "DDF00096",
            RuleTemplate.ERROR,
            "All primary endpoints must be referenced by a primary objective.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
