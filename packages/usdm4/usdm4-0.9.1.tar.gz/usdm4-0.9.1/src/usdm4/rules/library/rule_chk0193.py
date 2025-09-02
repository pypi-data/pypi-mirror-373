from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0193(RuleTemplate):
    """
    CHK0193: There must be exactly one sponsor study identifier (i.e., a study identifier whose scope is an organization that is identified as the organization for the sponsor study role).

    Applies to: StudyIdentifier
    Attributes: scope
    """

    def __init__(self):
        super().__init__(
            "CHK0193",
            RuleTemplate.ERROR,
            "There must be exactly one sponsor study identifier (i.e., a study identifier whose scope is an organization that is identified as the organization for the sponsor study role).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
