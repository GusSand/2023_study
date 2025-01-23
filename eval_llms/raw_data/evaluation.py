from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union, Iterable, Dict
import itertools
from execution import unsafe_execute, reliability_guard
import yaml
import numpy as np
import tqdm
from data import read_problems, stream_yaml, write_yaml
from execution import check_correctness, unsafe_execute
import textwrap
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import re
import textwrap
import contextlib

RED = "\033[91m"
RESET = "\033[0m"

def estimate_pass_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int
) -> np.ndarray:
    """
    Estimates pass@k of each problem and returns them in an array.
    """

    def estimator(n: int, c: int, k: int) -> float:
        """
        Calculates 1 - comb(n - c, k) / comb(n, k).
        """
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array([estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)])


HUMAN_EVAL = 'eval.yaml'

def format_code(code_string):
    # Remove leading/trailing whitespace and dedent
    formatted_code = textwrap.dedent(code_string.strip())
    # Replace escaped newlines with actual newlines
    formatted_code = formatted_code.replace('\\n', '\n')
    return formatted_code

def print_highlighted_code(code):
    highlighted_code = highlight(code, PythonLexer(), TerminalFormatter())
    print(highlighted_code)


def extract_readable_completion(code_string):
    formatted_code = textwrap.dedent(code_string)
    lines = formatted_code.split('\n')
    formatted_lines = [line for line in lines if line.strip() != '']
    formatted_code = '\n'.join(formatted_lines)
    return formatted_code


def evaluate_functional_correctness(
    sample_file: str,
    k: List[int] = [1, 5, 10],
    timeout: float = 20.0,
    problem_file: str = HUMAN_EVAL,
    log_file: str = None,
):
    problems = read_problems()
    results = []

    def process_samples():
        for sample in tqdm.tqdm(stream_yaml(sample_file)):
            task_id = sample["task_id"]
            completion = format_code(sample["completion"])
            result = unsafe_execute(problems[task_id], completion, timeout)
            
            # Log detailed results
            if log_file:
                with open(log_file, 'a') as f:
                    f.write(f"\n{'='*50}\nResults for {task_id}:\n{'='*50}\n")
                    f.write("Code:\n")
                    f.write(completion + "\n")
                    f.write("\nTest Results:\n")
                    failed_tests = [test for test in result.get("results", []) if not test["passed"]]

                    if failed_tests or "error" in result:
                        f.write(f"{'='*50}\nFailed Tests for {task_id}:\n{'='*50}\n")
                        if "error" in result:
                            f.write(f"Error: {result['error']}\n")
                        for test_result in failed_tests:
                            f.write(f"Test case {test_result['test_case']}: FAIL\n")
                            f.write(f"Input: {test_result['input']}\n")
                            f.write(f"Expected: {test_result['expected']}\n")
                            f.write(f"Actual: {test_result['actual']}\n")
                            f.write(f"Execution time: {test_result['execution_time']:.4f} seconds\n\n")
                        f.write(f"{'='*50}\n")
            
            results.append({
                "task_id": task_id,
                "completion": completion,
                "readable_completion": f"|\n{textwrap.indent(extract_readable_completion(completion), '  ')}",
                "passed": result["passed"],
                "results": result.get("results", []),
                "error": result.get("error", None),
                "execution_time": result.get("execution_time", None)
            })

    # Redirect stdout to the log file during processing
    if log_file:
        with open(log_file, 'w') as f:  # 'w' to start fresh
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                process_samples()
    else:
        process_samples()

    # Write results to YAML file
    out_file = f"{sample_file}_results.yaml"
    with open(out_file, 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    if log_file:
        with open(log_file, 'a') as f:
            f.write(f"\nResults written to {out_file}\n")

    # Calculate pass@k
    total = len(results)
    correct = sum(1 for result in results if result["passed"])
    
    pass_at_k = {}
    for k_value in k:
        if total >= k_value:
            pass_at_k[f"pass@{k_value}"] = estimate_pass_at_k(total, [correct], k_value)[0]

    return pass_at_k
