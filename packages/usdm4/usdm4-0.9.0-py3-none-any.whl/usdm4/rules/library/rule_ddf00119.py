from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00119(RuleTemplate):
    """
    DDF00119: A study design's trial types must be specified according to the extensible Trial Type Response (C66739) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyDesign
    Attributes: trialTypes
    """

    def __init__(self):
        super().__init__(
            "DDF00119",
            RuleTemplate.ERROR,
            "A study design's trial types must be specified according to the extensible Trial Type Response (C66739) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
