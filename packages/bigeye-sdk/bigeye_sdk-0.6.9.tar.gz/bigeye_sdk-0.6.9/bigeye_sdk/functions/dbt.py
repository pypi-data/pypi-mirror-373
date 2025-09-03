import json
import os
from pathlib import Path

from bigeye_sdk.model.dbt_manifest import DbtManifest


def parse_dbt_manifest(manifest_file: str) -> DbtManifest:
    if manifest_file == Path.cwd():
        manifest_file = os.path.join(Path.cwd(), "target/manifest.json")

    with open(manifest_file) as fh:
        data = json.load(fh)

    return DbtManifest(**data)
