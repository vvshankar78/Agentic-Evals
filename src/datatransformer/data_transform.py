import json
from typing import Any
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_config import load_config
from utils.load_mapping_schema import load_mapping_schema


def get_nested_value(d: dict, key_path: str) -> Any:
    """Safely get nested value using dot notation like 'metadata.arguments'."""
    keys = key_path.split('.')
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, {})
        else:
            return None
    return d or None


def replace_predicted_with_mapped(agent_data, mapping_schema):
    source_key = mapping_schema["source_key"]  # "predicted_function"
    field_mappings = mapping_schema["mappings"]

    output = []

    for item in agent_data:
        new_item = item.copy()
        mapped_functions = []

        for func in item.get(source_key, []):
            mapped_func = {}
            for source_field, target_field in field_mappings.items():
                value = get_nested_value(func, source_field)
                mapped_func[target_field] = value
            mapped_functions.append(mapped_func)

        # Replace original predicted_function with mapped one
        new_item[source_key] = mapped_functions
        output.append(new_item)

    return output

def main():
    config = load_config()
    data_transform_config = config["data_transformation"]

    dataset_path = Path(__file__).resolve().parents[1]
    input_file = os.path.join(dataset_path, data_transform_config["input_path"], data_transform_config["input_file"])
    output_file_json = os.path.join(dataset_path, data_transform_config["output_path"], data_transform_config["output_file_json"])
    output_file_jsonl = os.path.join(dataset_path, data_transform_config["output_path"], data_transform_config["output_file_jsonl"])

    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    mapping_schema = load_mapping_schema()

    mapped_output = replace_predicted_with_mapped(input_data, mapping_schema)

    with open(output_file_json, "w", encoding="utf-8") as f:
        json.dump(mapped_output, f, indent=2)
    
    # Write the mapped output as JSONL
    # jsonl_output_file = os.path.join(dataset_path, data_transform_config["output_path"], "agent_output_mapped.jsonl")
    with open(output_file_jsonl, "w", encoding="utf-8") as f:
        for item in mapped_output:
            f.write(json.dumps(item) + "\n")

    print("✅ 'predicted_function' replaced with mapped version and saved to agent_output_mapped.json")


if __name__ == "__main__":
    main()

