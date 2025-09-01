from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0273(RuleTemplate):
    """
    CHK0273: A study design's study phase must be specified according to the extensible Trial Phase Response (C66737) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: ObservationalStudyDesign, InterventionalStudyDesign
    Attributes: studyPhase
    """

    def __init__(self):
        super().__init__(
            "CHK0273",
            RuleTemplate.ERROR,
            "A study design's study phase must be specified according to the extensible Trial Phase Response (C66737) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
