import yaml
import os
import sys
import asyncio
from utils.load_config import load_config
# Add the paths to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'datagenerator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'datatransformer'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'evaluator'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'report'))

# from src.testing import generate_queries_from_groudtruth
from datagenerator import device_control_agent
from datatransformer import data_transform
from evaluator import eval_main
from reportgenerator import generate_report

if __name__ == "__main__":
    config = load_config()
    pipeline_config = config['pipeline']['steps']
    print(pipeline_config)
  
    if 'data_generation' in pipeline_config:
        print('executing device_control_agent')
        asyncio.run(device_control_agent.main())
        print('device_control_agent executed')

    if 'data_transformation' in pipeline_config:
       print('executing data_transform')
       data_transform.main()
       print('data_transform executed')

    if 'evaluation' in pipeline_config:
        print('executing eval_main')
        eval_main.main()
        print('eval_main executed')
    
    if 'reporting' in pipeline_config:
        print('executing report generation')
        generate_report.main()
        print('report generation executed')
        
    print('pipeline executed successfully')

  
 


