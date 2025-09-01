from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0245(RuleTemplate):
    """
    CHK0245: There must be exactly one study role with a code of sponsor.

    Applies to: StudyRole
    Attributes: code
    """

    def __init__(self):
        super().__init__(
            "CHK0245",
            RuleTemplate.ERROR,
            "There must be exactly one study role with a code of sponsor. ",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
