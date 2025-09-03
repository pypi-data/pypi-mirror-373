from pathlib import Path

import yaml

CONFIG = yaml.safe_load(open(Path(__file__).parent / "workflow.yaml"))

MOUNTS = CONFIG["mounts"]
LOKI_URLS = CONFIG["loki_urls"]
WORKFLOW_URLS = CONFIG["workflow_urls"]
PRODUCTS_URLS = CONFIG["products_urls"]

TEST_CONFIG = yaml.safe_load(open(Path(__file__).parent / "test_workflow.yaml"))

TEST_MOUNTS = TEST_CONFIG["mounts"]
