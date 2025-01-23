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
import contextlib
import logging

from typing import List
from dotenv import load_dotenv, find_dotenv
from concurrent.futures import ThreadPoolExecutor
import boto3

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



pattern = re.compile(r'```(?:[Pp]ython|[Pp]y)\s*([\s\S]+?)\s*```')
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_completion(task, model='gpt-3.5-turbo'):
    print(f"Getting completion for task: {task['task_id']} with model: {model}")
    prompt = task['prompt'] + "\n#Complete the function using python code only:\n"
    temp = 0.7
    max_tokens = 2048
    top_p = 1

    try:
        client = None
        result = None
        if model.startswith("gpt"):            
            client = OpenAI(
                #base_url=URL_BigBoyA100, 
                base_url=URL,
                api_key=os.environ['OPENAI_API_KEY'])
            
            completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an intelligent assistant. You must complete the python function given to you by the user. And you must follow the format they present when giving your answer!"},
                        {"role": "user", "content": prompt}
                 ],
                temperature=temp,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=0,
                presence_penalty=0
                )
            result = completion.choices[0].message.content

        
        elif "llama" in model.lower():
            client = boto3.client('bedrock-runtime', region_name='us-east-1',
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
            )

            response = client.invoke_model(
                modelId=model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "prompt": prompt,
                    "max_gen_len": max_tokens,  # Maximum length of generated response
                    "temperature": temp,  # Controls randomness of generation
                    "top_p": 1         # Controls diversity of generation
                })
            )
            result = json.loads(response['body'].read())['generation']
        else:
            raise ValueError(f"Invalid model: {model}")



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
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            completion = get_completion(task, model=model)
    return {'task_id': task['task_id'], 'completion': completion}


def get_results(model: str, num_runs: int = 1):
    all_pass_rates = []
    previous_results = None
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    print(f"\n{'='*50}")
    print(f"Starting {num_runs} runs with model: {model}")
    print(f"{'='*50}")
    
    for run in range(num_runs):
        # Set up logging for this run
        log_file = os.path.join('logs', f'{model}-run{run+1}.log')
        
        # Configure root logger to write to the log file
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        
        # Redirect stdout during task processing
        with open(log_file, 'a') as f:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                batch_size = 15
                batch = []
                run_results = []

                for task in iter_hval():
                    batch.append(task)
                    if len(batch) == batch_size:
                        with ThreadPoolExecutor() as executor:
                            futures = [executor.submit(process_command, task, model) for task in batch]
                            batch_results = [future.result() for future in futures]
                        run_results.extend(batch_results)
                        batch = []

                if batch:
                    with ThreadPoolExecutor() as executor:
                        futures = [executor.submit(process_command, task, model) for task in batch]
                        batch_results = [future.result() for future in futures]
                    run_results.extend(batch_results)

                # Save results
                out_file = os.path.join('raw_data', f'results-{model}-run{run+1}.yaml')
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                with open(out_file, 'w') as out_f:
                    yaml.dump(run_results, out_f, default_flow_style=False)

                current_results = evaluate_functional_correctness(out_file, log_file=log_file)
                all_pass_rates.append(current_results)

        # Print clean results for this run
        print(f"\nRun {run + 1}/{num_runs}:")
        for k in [1, 5, 10]:
            current_rate = current_results[f'pass@{k}']
            print(f"Pass@{k}: {current_rate:.2%}", end='')
            
            if previous_results is not None:
                prev_rate = previous_results[f'pass@{k}']
                diff = current_rate - prev_rate
                if diff != 0:
                    diff_str = f" ({'+' if diff > 0 else ''}{diff:.2%} from previous)"
                    print(diff_str, end='')
            print()
            
        previous_results = current_results
        print(f"Detailed logs written to: {log_file}")

    # Final summary
    print(f"\n{'='*50}")
    print("Final Summary")
    print(f"{'='*50}")
    
    for k in [1, 5, 10]:
        rates = [run_rates[f'pass@{k}'] for run_rates in all_pass_rates]
        avg_rate = sum(rates) / len(rates)
        min_rate = min(rates)
        max_rate = max(rates)
        print(f"\nPass@{k}:")
        print(f"  Average: {avg_rate:.2%}")
        print(f"  Min: {min_rate:.2%}")
        print(f"  Max: {max_rate:.2%}")

    return out_file

class CLI:
    def run(self, 
            model='gpt-4o-mini', 
            generate_results=False, 
            check_correctness=True, 
            k: List[int] = [1, 5, 10],
            timeout: float = 20.0,
            num_runs: int = 1):
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
            results_file = get_results(model=model, num_runs=num_runs)
        
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
    cli = CLI()
    fire.Fire(cli.run)
