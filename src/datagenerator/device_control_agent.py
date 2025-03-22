import asyncio
from dotenv import load_dotenv
import sys
import os
import yaml
from typing import Annotated
import json
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents.open_ai import AzureAssistantAgent
from semantic_kernel.contents import AuthorRole, ChatMessageContent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.functions import KernelArguments, kernel_function
# from plugins.device_control_plugin import DeviceControlPlugin
from plugins.control_plugins import TVControlPlugin, ACControlPlugin, RefrigeratorControlPlugin, DishwasherControlPlugin, WashingMachineControlPlugin

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from logging_tracing import setup_telemetry
load_dotenv(override=True)

setup_telemetry()

kernel = Kernel()
# kernel.add_plugin(DeviceControlPlugin(), plugin_name="device_control")
kernel.add_plugin(TVControlPlugin(), plugin_name="tv_control")
kernel.add_plugin(ACControlPlugin(), plugin_name="ac_control")
kernel.add_plugin(RefrigeratorControlPlugin(), plugin_name="refrigerator_control")
kernel.add_plugin(DishwasherControlPlugin(), plugin_name="dishwasher_control")
kernel.add_plugin(WashingMachineControlPlugin(), plugin_name="washingmachine_control")


service_id = "agent"
chat_completion_service = AzureChatCompletion(service_id=service_id)
kernel.add_service(chat_completion_service)

settings = kernel.get_prompt_execution_settings_from_service_id(
    service_id=service_id)
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

AGENT_NAME = "GAI_DEVICE_CONTROL"
AGENT_INSTRUCTIONS = "Answer questions about device control and perform the requested actions."
# Create the agent
agent = ChatCompletionAgent(
    kernel=kernel,
    name=AGENT_NAME,
    instructions=AGENT_INSTRUCTIONS,
    arguments=KernelArguments(settings=settings),
)

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

async def main():
    # Load configuration
    config_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.yaml')
    config = load_config(config_file_path)
    print('config', config)

    if config is None:
        raise ValueError("Configuration file not loaded properly.")

    # Define the chat history
    chat_history = ChatHistory()
    # Load user inputs from queries.txt
    queries_file_path =  config['data_generation']['input_path']
    queries_file_name = config['data_generation']['input_file']
    with open(os.path.join(os.path.dirname(__file__), '..', queries_file_path, queries_file_name), 'r') as file:
        user_inputs = [line.strip() for line in file.readlines()]

    print('queries_file_path', user_inputs)

    all_results = []

    for user_input in user_inputs:
        # Add the user input to the chat history
        chat_history.add_user_message(user_input)
        print(f"# User: '{user_input}'")

        agent_name: str | None = None
        response_content = ""
        output_data = {"query": user_input, "function_call_results": []}
        print("# Assistant - ", end="")
        async for content in agent.invoke_stream(chat_history):
            if (
                any(isinstance(item, (FunctionResultContent))
                        for item in content.items)
            ): 
                output_data["predicted_function"] = [item.dict() for item in content.items]
                # print(json.dumps(output_data, indent=2))
            if not agent_name:
                agent_name = content.name
                # print(f"agent name {agent_name}: '", end="")
            if (
                not any(isinstance(item, (FunctionCallContent, FunctionResultContent))
                        for item in content.items)
                and content.content.strip()
            ):
                response_content += content.content
                print(f"{content.content}", end="", flush=True)

        if response_content:
            output_data["response"] = response_content

        all_results.append(output_data)
        # print("output_data", output_data)

        # for message in chat_history.messages:
        #     if message.inner_content:
        #         print('--------------------------------------------------------')
        #         # print(f"# {message.author_role}: '{message.inner_content}'")
        #         print('message', message.to_dict())
        #         print('*************************************************')


    # Dump all results into a single JSON file

    output_file_path =  config['data_generation']['output_path']
    output_file_name = config['data_generation']['output_file']
    output_file_path = os.path.join(os.path.dirname(__file__), '..', output_file_path, output_file_name)
    with open(output_file_path, 'w') as json_file:
        json.dump(all_results, json_file, indent=2)

    # for message in chat_history.messages:
    #     if message.inner_content:
    #         print('--------------------------------------------------------')
    #         # print(f"# {message.author_role}: '{message.inner_content}'")
    #         print('message', message.to_dict())
    #         print('*************************************************')
    # print('chat history final', chat_history.messages)

if __name__ == "__main__":
    asyncio.run(main())
