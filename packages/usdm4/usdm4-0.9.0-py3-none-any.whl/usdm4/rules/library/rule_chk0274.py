from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0274(RuleTemplate):
    """
    CHK0274: A study design's study type must be specified using the Study Type Response (C99077) SDTM codelist.

    Applies to: ObservationalStudyDesign, InterventionalStudyDesign
    Attributes: studyType
    """

    def __init__(self):
        super().__init__(
            "CHK0274",
            RuleTemplate.ERROR,
            "A study design's study type must be specified using the Study Type Response (C99077) SDTM codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
