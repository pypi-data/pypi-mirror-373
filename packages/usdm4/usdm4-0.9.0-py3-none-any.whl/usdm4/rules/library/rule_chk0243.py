from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0243(RuleTemplate):
    """
    CHK0243: An study impact type must be specified according to the extensible study amendment impact type (Cxxxx) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyAmendmentImpact
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "CHK0243",
            RuleTemplate.ERROR,
            "An study impact type must be specified according to the extensible study amendment impact type (Cxxxx) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
