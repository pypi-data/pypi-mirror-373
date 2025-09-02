from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0185(RuleTemplate):
    """
    CHK0185: A study definition document type must be specifed according to the extensible XXX (Cnnn) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyDefinitionDocument
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "CHK0185",
            RuleTemplate.ERROR,
            "A study definition document type must be specifed according to the extensible XXX (Cnnn) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
