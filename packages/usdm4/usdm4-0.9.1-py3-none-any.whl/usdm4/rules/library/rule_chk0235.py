from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0235(RuleTemplate):
    """
    CHK0235: A masking is not expected to be defined for any study role in a study design with an open label blinding schema.

    Applies to: StudyRole
    Attributes: masking
    """

    def __init__(self):
        super().__init__(
            "CHK0235",
            RuleTemplate.ERROR,
            "A masking is not expected to be defined for any study role in a study design with an open label blinding schema.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
