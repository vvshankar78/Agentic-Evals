from run_eval import custom_eval
import os, sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_config import load_config


def main():
    eval_config = load_config()['evaluation']
    dataset_path = Path(__file__).resolve().parents[1]
    input_file = os.path.join(dataset_path, eval_config["input_path"], eval_config["input_file"])
    output_file = os.path.join(dataset_path, eval_config["output_path"], eval_config["output_file"])
    eval_name = eval_config["eval_name"]
    result = custom_eval(eval_name, input_file, output_file)

if __name__ == "__main__":
    main()
