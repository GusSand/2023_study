import json
import os
import re
import tqdm
import time
from openai import OpenAI
import yaml
from evaluation import evaluate_functional_correctness
import fire
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import psutil
import os
import requests
import traceback

from typing import List
from dotenv import load_dotenv, find_dotenv
from concurrent.futures import ThreadPoolExecutor

def print_memory_usage():
    process = psutil.Process(os.getpid())
    print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")



load_dotenv(find_dotenv())

URL = "https://api.openai.com/v1"
URL_local = "http://localhost:1234/v1"
URL_BigBoyA100 = "http://184.105.3.216:8000/v1"

client = OpenAI(base_url=URL_BigBoyA100)

HEADERS = {
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    "Content-Type": "application/yaml",
}

HUMAN_EVAL = 'eval.yaml'

OUT_FILE = os.environ['PWD'] + 'results-{}.yaml'

client = OpenAI(
    base_url=URL_BigBoyA100, 
    api_key=os.environ['OPENAI_API_KEY'])


pattern = re.compile(r'```(?:[Pp]ython|[Pp]y)\s*([\s\S]+?)\s*```')
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(task, model='gpt-3.5-turbo'):
    prompt = task['prompt'] + "\n#Complete the function using python code only:\n"

    #client = OpenAI(base_url=URL_BigBoyA100, api_key="dummy")  # vLLM doesn't need a real API key
    try:
        completion = client.completions.create(
            model=model,
        #     messages=[
        #         {"role": "system", "content": "You are an intelligent assistant. You must complete the python function given to you by the user. And you must follow the format they present when giving your answer!"},
        #         {"role": "user", "content": prompt}
        # ],
        prompt=prompt,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        #result = completion.choices[0].message.content
        result = completion.choices[0].text 
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Full traceback:")
        traceback.print_exc()

    match = pattern.search(result)
    
    if match:
        python_code = match.group(1)
    else:
        python_code = result

    return python_code


def iter_hval():
    with open(HUMAN_EVAL) as f:
        data = yaml.safe_load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        raise ValueError(f"Invalid data type: {type(data)}")

def process_command(task, model):
    completion = get_completion(task, model=model)
    return {'task_id': task['task_id'], 'completion': completion}


def get_results(model='gpt-4o-mini'):
    out_file = os.path.join('raw_data', f'results-{model}.yaml')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    results = []
    batch_size = 15
    batch = []

    with tqdm.tqdm(total=len(iter_hval())) as progress_bar:
        for task in iter_hval():
            batch.append(task)

            if len(batch) == batch_size:
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(process_command, task, model) for task in batch]
                    batch_results = [future.result() for future in futures]
                
                results.extend(batch_results)
                batch = []
                progress_bar.update(batch_size)

        # Process any remaining items in the batch
        if batch:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_command, task, model) for task in batch]
                batch_results = [future.result() for future in futures]
            
            results.extend(batch_results)
            progress_bar.update(len(batch))

    # Write results to YAML file
    with open(out_file, 'w') as out_f:
        yaml.dump(results, out_f, default_flow_style=False)

    print(f"Results written to {out_file}")
    return out_file

class CLI:
    def run(self, 
            model='gpt-4o-mini', 
            generate_results=False, 
            check_correctness=True, 
            k: List[int] = [1, 5, 10],
            timeout: float = 20.0):
        """
            Args: 
                model (str): The model to use for generating completions. Default is 'gpt-4o-mini'.
                generate_results (bool): Whether to run get_results. Default is False.
                check_correctness (bool): Whether to check functional correctness. Default is True.
                k (List[int]): The values of k for pass@k evaluation. Default is [1, 5, 10].
                timeout (float): Timeout for evaluation in seconds. Default is 20.0.
        """

        results_file = None
        if generate_results:
            results_file = get_results(model=model)
        
        if check_correctness:
            if results_file is None:
                results_file = OUT_FILE.format(model)
            
            pass_at_k_results = evaluate_functional_correctness(
                sample_file=results_file,
                k=k,
                timeout=timeout
            )
            
            print("\nDetailed Pass@k Results:")
            for k_value, v in pass_at_k_results.items():
                print(f"{k_value}: {v:.4f}")


if __name__ == '__main__':
    fire.Fire(CLI)
