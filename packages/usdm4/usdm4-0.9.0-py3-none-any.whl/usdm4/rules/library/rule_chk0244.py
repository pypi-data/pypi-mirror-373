from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0244(RuleTemplate):
    """
    CHK0244: An organization type must be specified according to the extensible organization type (C188724) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Organization
    Attributes: type
    """

    def __init__(self):
        super().__init__(
            "CHK0244",
            RuleTemplate.ERROR,
            "An organization type must be specified according to the extensible organization type (C188724) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
