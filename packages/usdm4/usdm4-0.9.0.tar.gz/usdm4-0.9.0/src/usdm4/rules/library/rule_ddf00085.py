from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00085(RuleTemplate):
    """
    DDF00085: Narrative content text is expected to be HTML formatted.

    Applies to: NarrativeContent
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "DDF00085",
            RuleTemplate.ERROR,
            "Narrative content text is expected to be HTML formatted.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
