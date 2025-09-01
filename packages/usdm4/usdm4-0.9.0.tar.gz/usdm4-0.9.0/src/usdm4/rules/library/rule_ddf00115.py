from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00115(RuleTemplate):
    """
    DDF00115: Every study version must have a title of type \"Official Study Title\".

    Applies to: StudyVersion
    Attributes: titles
    """

    def __init__(self):
        super().__init__(
            "DDF00115",
            RuleTemplate.ERROR,
            'Every study version must have a title of type "Official Study Title".',
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
