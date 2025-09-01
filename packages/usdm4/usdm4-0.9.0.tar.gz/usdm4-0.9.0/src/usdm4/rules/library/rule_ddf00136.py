from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00136(RuleTemplate):
    """
    DDF00136: An encounter's contact modes must be specified according to the Mode of Subject Contact (C171445) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Encounter
    Attributes: contactModes
    """

    def __init__(self):
        super().__init__(
            "DDF00136",
            RuleTemplate.ERROR,
            "An encounter's contact modes must be specified according to the Mode of Subject Contact (C171445) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
