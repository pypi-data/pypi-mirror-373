from typing import TypedDict, Dict, List
import json

class Settings(TypedDict):
    sync_dirs: Dict[str,List[str]]
    db_dir: str

def parse_settings(settings_file: str) -> Settings:
    with open(settings_file, 'r') as file:
        return json.load(file)
