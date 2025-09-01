import os
from .yaml_config import YamlConfig

YAML_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")
YAML_CONFIG = YamlConfig(YAML_FILE)
APP_NAME = YAML_CONFIG.get_value('app_name')
WITH_CONSOLE_LOG = YAML_CONFIG.get_value('log.with_console')
LOG_FILE = YAML_CONFIG.get_value('log.file', expanding_user=True, make_dir=True)
DB_FILE = YAML_CONFIG.get_value('db_file', expanding_user=True, make_dir=True)
DATA_DIR = YAML_CONFIG.get_value('data_dir', expanding_user=True, make_dir=True)
