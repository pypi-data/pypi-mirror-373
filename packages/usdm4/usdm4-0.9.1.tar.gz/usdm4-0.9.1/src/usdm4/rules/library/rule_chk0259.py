from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0259(RuleTemplate):
    """
    CHK0259: An interventional study design's sub types must be specified according to the extensible Trial Type Response (C66739) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: InterventionalStudyDesign
    Attributes: subTypes
    """

    def __init__(self):
        super().__init__(
            "CHK0259",
            RuleTemplate.ERROR,
            "An interventional study design's sub types must be specified according to the extensible Trial Type Response (C66739) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
