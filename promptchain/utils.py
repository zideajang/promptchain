import json
from datetime import datetime
import pytz
import numpy as np
from pydantic import BaseModel
from rich.console import Console

console = Console()

DEBUG = False


def create_example_from_model(model: BaseModel) -> str:
    example_data = {}
    for field_name, field in model.model_fields.items():
        if not field.examples:
            raise ValueError(f"字段 '{field_name}' 在 Pydantic 模型中缺少 'examples' 值。请为所有字段提供示例。")
        example_data[field_name] = field.examples[0]
    return json.dumps(example_data, ensure_ascii=False, indent=2)

def printd(*args, **kwargs):
    if DEBUG:
        console.print(*args, **kwargs)

def get_local_time():
    # Get the current time in UTC
    current_time_utc = datetime.now(pytz.utc)

    sf_time_zone = pytz.timezone('Asia/Shanghai')
    local_time = current_time_utc.astimezone(sf_time_zone)

    # You may format it as you desire, including AM/PM
    formatted_time = local_time.strftime("%Y-%m-%d %I:%M:%S %p %Z%z")

    return formatted_time

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

if __name__ == "__main__":
    get_local_time = get_local_time()
    console.print(get_local_time)
