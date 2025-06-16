import json

class JsonHandler:
    @staticmethod
    def load_json(file_path):
        """Load JSON file from given path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load JSON file: {str(e)}")    @staticmethod
    def save_json(file_path, data):
        """Save data to JSON file in Warudo format (single line, no indentation)"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            raise Exception(f"Failed to save JSON file: {str(e)}")
