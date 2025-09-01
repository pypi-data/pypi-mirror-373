from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00122(RuleTemplate):
    """
    DDF00122: A study design's characteristics must be specified according to the Study design characteristics (C207416) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: StudyDesign
    Attributes: characteristics
    """

    def __init__(self):
        super().__init__(
            "DDF00122",
            RuleTemplate.ERROR,
            "A study design's characteristics must be specified according to the Study design characteristics (C207416) DDF codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
