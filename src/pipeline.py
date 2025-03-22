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

from datagenerator import generate_queries_from_groudtruth
from datagenerator import device_control_agent


if __name__ == "__main__":
    config = load_config()
    pipeline_config = config['pipeline']['steps']
    print(pipeline_config)

    if 'generate_queries' in pipeline_config:
        print('executing generate_queries_from_groundtruth')
        generate_queries_from_groudtruth.extract_queries()
        print('generate_queries_from_groundtruth executed')

  
    if 'data_generation' in pipeline_config:
        print('executing device_control_agent')
        asyncio.run(device_control_agent.main())
        print('device_control_agent executed')

    # # Run data_transform.py
    # from datatransformer import data_transform
    # print('executing data_transform')
    # data_transform.main()
    # print('data_transform executed')

    # # Run eval_main.py
    # from evaluator import eval_main
    # print('executing eval_main')
    # eval_main.main()
    # print('eval_main executed')


    # from report import generate_report
    # print('executing generate_report')
    # generate_report.main()
    # print('generate_report executed')


