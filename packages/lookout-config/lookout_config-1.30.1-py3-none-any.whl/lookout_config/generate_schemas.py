import os
from pathlib import Path
import json
from lookout_config import LookoutConfig


def generate_schemas():
    """Generates the schemas for the config files"""
    SCHEMAS_PATH = Path(os.path.dirname(__file__)) / "schemas"
    with open(SCHEMAS_PATH / "lookout.schema.json", "w") as f:
        main_model_schema = LookoutConfig.model_json_schema()
        json.dump(main_model_schema, f, indent=2)


if __name__ == "__main__":
    generate_schemas()
