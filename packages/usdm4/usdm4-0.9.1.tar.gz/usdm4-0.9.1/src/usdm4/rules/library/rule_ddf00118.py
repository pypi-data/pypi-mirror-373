from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00118(RuleTemplate):
    """
    DDF00118: A study design's trial intent types must be specified according to the extensible Trial Intent Type Response (C66736) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyDesign
    Attributes: trialIntentTypes
    """

    def __init__(self):
        super().__init__(
            "DDF00118",
            RuleTemplate.ERROR,
            "A study design's trial intent types must be specified according to the extensible Trial Intent Type Response (C66736) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
