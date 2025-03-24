# Evaluation of Agentic Systems using Azure AI Foundry

Agents are AI models with memories that communicate via messages. They can interact with themselves, other agents, or the human user, these messages include text, multimodalities, and tools or function calls, forming a chat history/thread/trajectory.

Agentic systems can range from single agents with tool calling to complex multi-agent systems that communicate to complete tasks. Building an evaluation pipeline for such systems starts with creating ground truth datasets based on real-world usage. 

This framework provides a step-by-step approch to building a pipeline to Evaluate agentic system using Azure AI Foundry, using single agent with multiple plugins from Sematic Kernel as an example. This repository provides a reporting framework using html report locally to analyze, visualize and share the evaluation results to various stake holders. 

## 1. Agentic Evaluation Pipeline (Inner Loop)
Inputs are fed to agentic systems, and outputs—either end responses or inner workings like function calls, agent selection, and communication—are evaluated.
Extracting these inner details is crucial for robust evaluation. Evaluators compare predicted data to ground truth data, scoring them accordingly. 
Currently, specialized evaluators for agentic systems need to be custom-built, as existing AI foundry tools support RAG and chatbot applications only. 
Finally, evaluation results are stored and visualized both in AI Foundry's evaluator dashboard and a custom HTML Report built using Jinja2 template. 

Agentic-Eval-Pipeline is a Python-based framework for building and evaluating agentic systems.


## 2. Folder Structure

The repository is organized as follows:

```
project-root/
│
├── src/                # Source code for the framework
│   ├── __init__.py     # Makes src a package
│   ├── pipeline.py     # Core pipeline logic
│   ├── data_generator/ # Code for generating data
│   ├── data_transforms/ # Code for transforming data
│   ├── evaluator/      # Code for evaluation logic
│   ├── datasets/       # Code for dataset management
│   └── report_generator/ # Code for generating reports
│
├── config/             # Configuration files
│   ├── settings.py     # General settings
│   └── config.yaml     # YAML configuration file
│
├── assets/             # Assets like images or diagrams
│   └── Eval-pipeline.png # Diagram of the evaluation pipeline
│
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # Project documentation
└── LICENSE             # License file
```

## 3. Prerequisites
Before getting started, ensure you have the following:

- Azure Subscription: Access to an Azure subscription with the necessary permissions.
- Azure CLI: Installed and configured on your local machine.
- Azure AI Foundry - Hub and Project created with model (GPT4o) deployed and Blob storage link set up. Refer [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-ai-foundry#work-in-an-azure-ai-foundry-project).
- Python 3.11 or above
- Git: For version control and cloning the repository.


## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/agentic-evals.git
   ```
2. Navigate to the project directory:
   ```bash
   cd agentic-evals
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the pipeline:
   ```bash
   python src/pipeline.py
   ```
2. Customize the pipeline by modifying `src/pipeline.py` or adding new modules under `src/`.

## Contributing
...existing code...

## License
...existing code...

## Links
AI Foundry: https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-ai-foundry#work-in-an-azure-ai-foundry-project