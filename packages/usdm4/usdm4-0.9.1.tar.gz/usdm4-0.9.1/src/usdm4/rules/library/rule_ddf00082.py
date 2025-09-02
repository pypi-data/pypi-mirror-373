import os
import pathlib
from usdm3.rules.library.rule_ddf00082 import RuleDDF00082 as V3Rule
from usdm3.rules.library.schema.schema_location import SchemaErrorLocation
from usdm3.rules.library.schema.schema_validation import (
    SchemaValidation,
    ValidationError,
)
from usdm3.data_store.data_store import DataStore


class RuleDDF00082(V3Rule):
    def validate(self, config: dict) -> bool:
        try:
            data: DataStore = config["data"]
            path = self._schema_path()
            validator = SchemaValidation(path)
            validator.validate_file(data.filename, "Wrapper-Input")
            return True
        except ValidationError as e:
            location = SchemaErrorLocation(e.json_path, e.instance)
            self._errors.add(f"Message: {e.message}\nContext: {e.context}", location)
            return False

    def _schema_path(self) -> str:
        root = pathlib.Path(__file__).parent.resolve()
        return os.path.join(root, "schema/usdm_v4-0-0.json")
