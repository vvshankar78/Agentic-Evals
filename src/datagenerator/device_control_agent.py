import asyncio
import json
import sys, os
from pathlib import Path
import yaml
from dotenv import load_dotenv
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.kernel import Kernel
from plugins.control_plugins import (
    TVControlPlugin,
    ACControlPlugin,
    RefrigeratorControlPlugin,
    DishwasherControlPlugin,
    WashingMachineControlPlugin
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from logging_tracing import setup_telemetry

# Load environment variables from .env file
load_dotenv(override=True)

# Setup logging and telemetry
setup_telemetry()

# Initialize the Semantic Kernel and register device control plugins
kernel = Kernel()
kernel.add_plugin(TVControlPlugin(), plugin_name="tv_control")
kernel.add_plugin(ACControlPlugin(), plugin_name="ac_control")
kernel.add_plugin(RefrigeratorControlPlugin(), plugin_name="refrigerator_control")
kernel.add_plugin(DishwasherControlPlugin(), plugin_name="dishwasher_control")
kernel.add_plugin(WashingMachineControlPlugin(), plugin_name="washingmachine_control")

# Register the Azure OpenAI chat completion service
service_id = "agent"
chat_completion_service = AzureChatCompletion(service_id=service_id)
kernel.add_service(chat_completion_service)

# Configure prompt execution settings
settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# Define the conversational agent
AGENT_NAME = "GAI_DEVICE_CONTROL"
AGENT_INSTRUCTIONS = "Answer questions about device control and perform the requested actions."
agent = ChatCompletionAgent(
    kernel=kernel,
    name=AGENT_NAME,
    instructions=AGENT_INSTRUCTIONS,
    arguments=KernelArguments(settings=settings),
)

def load_config(config_file: str) -> dict:
    """Load YAML configuration from the given file path."""
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

async def main():
    # Resolve base and configuration paths
    base_path = Path(__file__).resolve().parents[2]
    config_path = base_path / 'config' / 'config.yaml'
    config = load_config(str(config_path))

    if config is None:
        raise ValueError("Configuration file not loaded properly.")

    # Read user input queries from file
    dataset_path = Path(__file__).resolve().parents[1]
    queries_path = dataset_path / config['data_generation']['input_path'] / config['data_generation']['input_file']
    with open(queries_path, 'r') as file:
        user_inputs = [line.strip() for line in file.readlines()]

    chat_history = ChatHistory()
    all_results = []

    # Process each input through the agent
    for user_input in user_inputs:
        chat_history.add_user_message(user_input)

        response_content = ""
        output_data = {"query": user_input}

        async for content in agent.invoke_stream(chat_history):
            # Capture any function result returned by the agent
            if any(isinstance(item, FunctionResultContent) for item in content.items):
                output_data["predicted_function"] = [item.dict() for item in content.items]

            # Capture plain text response (not function call or result)
            if not any(isinstance(item, (FunctionCallContent, FunctionResultContent)) for item in content.items) and content.content.strip():
                response_content += content.content

        if response_content:
            output_data["response"] = response_content
            print('response :', output_data['query'], '\n', output_data['response'])

        all_results.append(output_data)

    # Write all output results to a JSON file
    output_path = dataset_path / config['data_generation']['output_path'] / config['data_generation']['output_file']
    with open(output_path, 'w') as json_file:
        json.dump(all_results, json_file, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
