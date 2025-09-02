from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0191(RuleTemplate):
    """
    CHK0191: All abbreviations defined for a study version must be unique.

    Applies to: Abbreviation
    Attributes: abbreviation
    """

    def __init__(self):
        super().__init__(
            "CHK0191",
            RuleTemplate.ERROR,
            "All abbreviations defined for a study version must be unique.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
