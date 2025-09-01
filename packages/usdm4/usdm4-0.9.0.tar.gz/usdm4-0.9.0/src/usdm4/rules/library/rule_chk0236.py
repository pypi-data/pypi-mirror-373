from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0236(RuleTemplate):
    """
    CHK0236: A masking is expected to be defined for at least two study roles in a study design with a double blind blinding schema.

    Applies to: StudyRole
    Attributes: masking
    """

    def __init__(self):
        super().__init__(
            "CHK0236",
            RuleTemplate.ERROR,
            "A masking is expected to be defined for at least two study roles in a study design with a double blind blinding schema.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
