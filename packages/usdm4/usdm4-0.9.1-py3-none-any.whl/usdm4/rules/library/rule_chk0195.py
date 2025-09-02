from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0195(RuleTemplate):
    """
    CHK0195: Every identifier must be unique within the scope of an identified organization.

    Applies to: StudyIdentifier, ReferenceIdentifier, AdministrableProductIdentifier
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "CHK0195",
            RuleTemplate.ERROR,
            "Every identifier must be unique within the scope of an identified organization.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
