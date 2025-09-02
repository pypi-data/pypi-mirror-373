from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00054(RuleTemplate):
    """
    DDF00054: Within an encounter there must be no duplicate contact modes.

    Applies to: Encounter
    Attributes: contactModes
    """

    def __init__(self):
        super().__init__(
            "DDF00054",
            RuleTemplate.ERROR,
            "Within an encounter there must be no duplicate contact modes.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
