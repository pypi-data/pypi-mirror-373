from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0237(RuleTemplate):
    """
    CHK0237: A masking is expected to be defined for at least one study role in a study design with a blinding schema that is not open label or double blind.

    Applies to: StudyRole
    Attributes: masking
    """

    def __init__(self):
        super().__init__(
            "CHK0237",
            RuleTemplate.ERROR,
            "A masking is expected to be defined for at least one study role in a study design with a blinding schema that is not open label or double blind.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
