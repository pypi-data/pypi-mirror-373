from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00116(RuleTemplate):
    """
    DDF00116: A study version's study type must be specified using the Study Type Response (C99077) SDTM codelist.

    Applies to: StudyVersion
    Attributes: studyType
    """

    def __init__(self):
        super().__init__(
            "DDF00116",
            RuleTemplate.ERROR,
            "A study version's study type must be specified using the Study Type Response (C99077) SDTM codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
