from src.utils.db_api.postgresql import Database
from src.config import load_config

config = load_config(".env")
db = Database(config)