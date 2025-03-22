import yaml
import os
import sys
import asyncio

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    # config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    # config = load_config(config_file_path)

    # Add the paths to the system path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'datagenerator'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'datatransformer'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'evaluator'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'reportgenerator'))

    # Run device_control_agent.py
    from datagenerator import device_control_agent
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


