from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0170(RuleTemplate):
    """
    CHK0170: Within an encounter, if more environmental settings are defined, they must be distinct.

    Applies to: Encounter
    Attributes: environmentalSettings
    """

    def __init__(self):
        super().__init__(
            "CHK0170",
            RuleTemplate.ERROR,
            "Within an encounter, if more environmental settings are defined, they must be distinct.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
