from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0269(RuleTemplate):
    """
    CHK0269: An observational study design's sampling method must be specified according to the extensible Observational Study Sampling Method (C127260) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: ObservationalStudyDesign
    Attributes: samplingMethod
    """

    def __init__(self):
        super().__init__(
            "CHK0269",
            RuleTemplate.ERROR,
            "An observational study design's sampling method must be specified according to the extensible Observational Study Sampling Method (C127260) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
