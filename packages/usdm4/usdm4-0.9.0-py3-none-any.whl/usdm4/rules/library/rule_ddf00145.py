from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00145(RuleTemplate):
    """
    DDF00145: A unit must be coded according to the extensible unit (C71620) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Range, Quantity
    Attributes: unit
    """

    def __init__(self):
        super().__init__(
            "DDF00145",
            RuleTemplate.ERROR,
            "A unit must be coded according to the extensible unit (C71620) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
