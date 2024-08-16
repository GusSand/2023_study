import json
import os
import re
import tqdm
import time
from openai import OpenAI
import yaml
from evaluation import evaluate_functional_correctness
import fire

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from typing import List
from dotenv import load_dotenv, find_dotenv
from concurrent.futures import ThreadPoolExecutor


load_dotenv(find_dotenv())

URL = "https://api.openai.com/v1"
URL_local = "http://localhost:1234/v1"

client = OpenAI(base_url=URL)

HEADERS = {
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
    "Content-Type": "application/yaml",
}

HUMAN_EVAL = 'eval.yaml'

OUT_FILE = os.environ['PWD'] + 'results-{}.yaml'


pattern = re.compile(r'```(?:[Pp]ython|[Pp]y)\s*([\s\S]+?)\s*```')
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(task, model='gpt-3.5-turbo'):
    prompt = task['prompt'] + "\n#Complete the function using python code only:\n"
    completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are an intelligent . You must complete the python function given to you by the user. And you must follow the format they present when giving your answer!"},
        {"role": "user", "content": prompt}]
    )

    result = (completion.choices[0].message.content)
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
    out_file = OUT_FILE.format(model)

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
        Run the evaluation pipeline.
        
        :param model: The model to use for generating completions.
        :param get_results: Whether to run get_results.
        :param check_correctness: Whether to check functional correctness.
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
