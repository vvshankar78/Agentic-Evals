import os
from dotenv import load_dotenv
from azure.ai.evaluation import evaluate
from azure.ai.evaluation import GroundednessEvaluator, FluencyEvaluator
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
# credential = DefaultAzureCredential()
from azure.ai.projects import AIProjectClient
# from evaluator.evaluator_repo.agent_function_call_evaluator import FunctionCallEvaluator
from azure.ai.evaluation._evaluators._fluency._fluency import FluencyEvaluator
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration
from evaluator_repo.end_to_end_function_call_eval import EndToEndFunctionCallEvaluator

load_dotenv(override=True)

def custom_eval(name, data_path, output_path):
    """
    Evaluate the model using the given data and column mapping.
    """
    from azure.identity import DefaultAzureCredential
    credential = DefaultAzureCredential()

    ## Create an instance of the AIProjectClient class
    project = AIProjectClient.from_connection_string(
        conn_str=f"{os.environ['CONNECTION_STRING']}",
        credential=credential,
    )
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
        "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
    }

    # Initialize FluencyEvaluator with model configuration
    # fluency_eval = FluencyEvaluator(model_config=model_config)
    # function_call_eval = FunctionCallEvaluator()
    end_to_end_function_call_eval = EndToEndFunctionCallEvaluator()
    

    ## Evaluate the data using the coverage evaluator
    result = evaluate(
        data=data_path,
        evaluation_name=name,
        evaluators={
            # "function_call": function_call_eval,
            # "fluency": fluency_eval,
            "end_to_end_function_call": end_to_end_function_call_eval
        },
        evaluator_config={"end_to_end_function_call": {"column_mapping": {
                "query": "${data.query}",
                "expected": "${data.expected_function}",
                "predicted": "${data.predicted_function}", 
                "response": "${data.predicted_response}"
            }}},
        azure_ai_project = project.scope,
        output_path=output_path,
    )
    return result