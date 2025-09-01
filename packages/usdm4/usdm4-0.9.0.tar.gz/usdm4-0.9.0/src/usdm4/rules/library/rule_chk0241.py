from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0241(RuleTemplate):
    """
    CHK0241: A study definition document version must not be referenced more than once by the same study design.

    Applies to: ObservationalStudyDesign, InterventionalStudyDesign
    Attributes: documentVersions
    """

    def __init__(self):
        super().__init__(
            "CHK0241",
            RuleTemplate.ERROR,
            "A study definition document version must not be referenced more than once by the same study design.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
