import yaml
from typing import List, Dict

def load_yaml_tests(file_path: str) -> Dict[str, Dict]:
    with open(file_path, 'r') as file:
        test_data = yaml.safe_load(file)
    
    return {item ['task_id']: item for item in test_data}

def get_test_cases(problem: Dict) -> List[Dict]:
    return problem['tests']

def print_prompts(yaml_file: str):
    with open(yaml_file, 'r') as file: 
        data = yaml.safe_load(file)

    for task in data:
        print(f"Task ID: {task['task_id']}")
        print(f"Prompt")
        print(task['prompt'])
        print("\n" + "="*50 + "\n") # print a line of equal signs

    

# funciton that prints all the task_id/prompts


# print all of them

#print(load_yaml_tests('eval.yaml'))
print_prompts('eval.yaml')
