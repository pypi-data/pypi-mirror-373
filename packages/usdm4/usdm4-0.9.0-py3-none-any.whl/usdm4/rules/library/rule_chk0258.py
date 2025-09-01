from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0258(RuleTemplate):
    """
    CHK0258: An interventional study design's intent types must be specified according to the extensible Trial Intent Type Response (C66736) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: InterventionalStudyDesign
    Attributes: intentTypes
    """

    def __init__(self):
        super().__init__(
            "CHK0258",
            RuleTemplate.ERROR,
            "An interventional study design's intent types must be specified according to the extensible Trial Intent Type Response (C66736) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
