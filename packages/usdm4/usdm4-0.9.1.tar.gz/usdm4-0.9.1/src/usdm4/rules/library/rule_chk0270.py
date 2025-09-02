from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0270(RuleTemplate):
    """
    CHK0270: A observational study design's sub types must be specified according to the (Cxxxx) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: ObservationalStudyDesign
    Attributes: subTypes
    """

    def __init__(self):
        super().__init__(
            "CHK0270",
            RuleTemplate.ERROR,
            "A observational study design's sub types must be specified according to the (Cxxxx) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
