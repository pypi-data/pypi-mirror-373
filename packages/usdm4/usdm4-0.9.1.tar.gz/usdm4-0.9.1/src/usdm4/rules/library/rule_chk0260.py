from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0260(RuleTemplate):
    """
    CHK0260: A study design's intervention model must be specified according to the extensible Intervention Model Response (C99076) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: InterventionalStudyDesign
    Attributes: model
    """

    def __init__(self):
        super().__init__(
            "CHK0260",
            RuleTemplate.ERROR,
            "A study design's intervention model must be specified according to the extensible Intervention Model Response (C99076) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
