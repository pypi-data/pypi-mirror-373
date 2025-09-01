from usdm3.rules.library.rule_ddf00140 import RuleDDF00140 as V3Rule


class RuleDDF00140(V3Rule):
    def validate(self, config: dict) -> bool:
        return self._ct_check(config, "Organization", "type")
