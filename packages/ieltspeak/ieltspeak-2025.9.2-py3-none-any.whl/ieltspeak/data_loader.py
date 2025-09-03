import json
import random
import importlib.resources
from pathlib import Path
from typing import Dict, Any, Union


class TopicDataLoader:
    """处理JSON数据文件的加载和查询"""

    def __init__(self) -> None:
        self.data_cache: Dict[str, Dict[str, Any]] = {}

    def _load_data_file(self, data_file: str) -> Dict[str, Any]:
        """加载数据文件，优先使用包资源，失败时回退到文件系统"""
        if data_file in self.data_cache:
            return self.data_cache[data_file]

        try:
            # 优先使用包内资源
            data_content = (
                importlib.resources.files("data")
                .joinpath(data_file)
                .read_text(encoding="utf-8")
            )
            data = json.loads(data_content)
        except Exception:
            # 回退到文件系统（同级目录的data文件夹）
            try:
                json_path = Path(__file__).parent / "data" / data_file
                if not json_path.exists():
                    raise FileNotFoundError(f"Data file not found at {json_path}")
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                raise ValueError(f"Error reading data file: {e}")

        self.data_cache[data_file] = data
        return data

    def get_topic(
        self, part: Union[str, int], category: str
    ) -> Union[Dict[str, Any], str]:
        """获取指定部分和类别的随机话题"""
        # 确定数据文件名
        # To handle both string and integer inputs, convert part to string for comparison
        str_part = str(part)
        if str_part == "1":
            data_file = "ielts_part0.json"
        elif str_part == "2and3":
            data_file = "ielts_part1.json"
        else:
            return f"Error: Invalid part '{part}'. Please use '1' or '2and3'."

        try:
            data = self._load_data_file(data_file)
        except ValueError as e:
            return str(e)

        # 验证类别存在
        if category not in data.get("data", {}):
            available_categories = ", ".join(data.get("data", {}).keys())
            return f"Error: Category '{category}' not found. Available categories: {available_categories}"

        topics = data["data"][category]
        if not topics:
            return f"Error: No topics found for category '{category}'."

        # 返回包含part信息和随机话题的字典
        return {
            "part_info": {
                "part": data.get("part", "N/A"),
                "part_name": data.get("part_name", "N/A"),
            },
            "topic": random.choice(topics),
        }
