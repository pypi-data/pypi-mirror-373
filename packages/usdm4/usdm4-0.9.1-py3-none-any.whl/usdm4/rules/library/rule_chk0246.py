from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0246(RuleTemplate):
    """
    CHK0246: The sponsor study role must point to exactly one organization.

    Applies to: StudyRole
    Attributes: organizations
    """

    def __init__(self):
        super().__init__(
            "CHK0246",
            RuleTemplate.ERROR,
            "The sponsor study role must point to exactly one organization.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
