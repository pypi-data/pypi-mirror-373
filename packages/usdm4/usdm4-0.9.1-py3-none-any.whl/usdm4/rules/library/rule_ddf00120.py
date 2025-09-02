from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00120(RuleTemplate):
    """
    DDF00120: A study design's intervention model must be specified according to the extensible Intervention Model Response (C99076) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyDesign
    Attributes: interventionModel
    """

    def __init__(self):
        super().__init__(
            "DDF00120",
            RuleTemplate.ERROR,
            "A study design's intervention model must be specified according to the extensible Intervention Model Response (C99076) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
