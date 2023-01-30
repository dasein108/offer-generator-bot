import ujson
from typing import Any, Dict


class JsonDB:
    file_name: str = "json_db.json"

    @staticmethod
    def load_data():
        try:
            with open(JsonDB.file_name) as f:
                return ujson.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def save_data(data: Dict[str, Any]):
        with open(JsonDB.file_name, 'w') as f:
            ujson.dump(data, f, indent=4)

    @staticmethod
    def save_user_data(user_id: int, key: str, value: Any):
        data = JsonDB.load_data()
        if user_id not in data:
            data[user_id] = {}

        data[user_id][key] = value

        JsonDB.save_data(data)

    @staticmethod
    def load_user_data(user_id: int):
        data = JsonDB.load_data()
        if user_id not in data:
            return {}

        return data[user_id]

