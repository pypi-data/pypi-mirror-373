from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00038(RuleTemplate):
    """
    DDF00038: When included in text, references to items specified in the dictionary must be specified in the correct format. They must start with <usdm:tag, end with either '/>'', and must contain name=\"parametername\" (where \"parametername\"  contain only letters, numbers or underscores).

    Applies to: EligibilityCriterion, Characteristic, Condition, Objective, Endpoint
    Attributes: text
    """

    def __init__(self):
        super().__init__(
            "DDF00038",
            RuleTemplate.ERROR,
            'When included in text, references to items specified in the dictionary must be specified in the correct format. They must start with <usdm:tag, end with either \'/>\'\', and must contain name="parametername" (where "parametername"  contain only letters, numbers or underscores).',
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
