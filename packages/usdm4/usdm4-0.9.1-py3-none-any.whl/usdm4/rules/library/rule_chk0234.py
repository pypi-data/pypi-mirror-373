from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0234(RuleTemplate):
    """
    CHK0234: A study role must not reference both assigned persons and organizations.

    Applies to: StudyRole
    Attributes: assignedPersons, organizations
    """

    def __init__(self):
        super().__init__(
            "CHK0234",
            RuleTemplate.ERROR,
            "A study role must not reference both assigned persons and organizations.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
