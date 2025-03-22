import json
import os
import sys
from pathlib import Path
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_config import load_config

def extract_queries():
    # Load configuration from YAML file
    config = load_config()

    # Define file paths
    dataset_path = Path(__file__).resolve().parents[1]
    input_file = os.path.join(dataset_path, config["generate_queries"]["input_path"], config["generate_queries"]["input_file"])
    output_file = os.path.join(dataset_path, config["generate_queries"]["output_path"], config["generate_queries"]["output_file"])  
    num_of_queries = config["generate_queries"]["num_of_queries"]
    query_key = config["generate_queries"]["query_key"]

    # Read the ground_truth.json file
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract the values of the "query" key
    queries = []
    for item in data:
        if "query" in item:
            queries.append(item[query_key])
            if len(queries) >= num_of_queries:
                break

    # Write the queries to queries.txt
    with open(output_file, "w", encoding="utf-8") as f:
        for query in queries:
            f.write(query + "\n")

    print(f"Queries have been written to {output_file}")

# Make this script executable and importable
if __name__ == "__main__":
    extract_queries()
