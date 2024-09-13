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

def evaluate_functional_correctness(
    sample_file: str,
    k: List[int] = [1, 5, 10],
    timeout: float = 20.0,
    problem_file: str = HUMAN_EVAL,
):
    problems = read_problems()
    results = []

    for sample in tqdm.tqdm(stream_yaml(sample_file)):
        task_id = sample["task_id"]
        completion = format_code(sample["completion"])
        result = unsafe_execute(problems[task_id], completion, timeout)
        
        # print(f"\n{RED}{'='*50}\nResults for {task_id}:\n{'='*50}{RESET}\n")
        # print("Code:")
        # print_highlighted_code(completion)
        # print("\nTest Results:")
        failed_tests = [test for test in result.get("results", []) if not test["passed"]]

        if failed_tests or "error" in result:
            print(f"{RED}{'='*50}\nResults for {task_id}:\n{'='*50}{RESET}\n")
            print("Code:")
            print_highlighted_code(completion)
            print("\nTest Results:")
            if "error" in result:
                print(f"{RED}Error: {result['error']}{RESET}")
            for test_result in failed_tests:
                print(f"{RED}Test case {test_result['test_case']}: FAIL{RESET}")
                print(f"Input: {test_result['input']}")
                print(f"Expected: {test_result['expected']}")
                print(f"Actual: {test_result['actual']}")
                print(f"Execution time: {test_result['execution_time']:.4f} seconds\n")

        
            print(f"{RED}{'='*50}{RESET}\n")
        
        results.append({
            "task_id": task_id,
            "completion": completion,
            "passed": result["passed"],
            "results": result.get("results", []),
            "error": result.get("error", None),
            "execution_time": result.get("execution_time", None)
        })

    # Write results to YAML file
    out_file = f"{sample_file}_results.yaml"
    with open(out_file, 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    print(f"Results written to {out_file}")

    # Calculate pass@k
    total = len(results)
    correct = sum(1 for result in results if result["passed"])
    
    pass_at_k = {}
    for k_value in k:
        if total >= k_value:
            # We're treating all problems as one here, so we pass a single-element list
            pass_at_k[f"pass@{k_value}"] = estimate_pass_at_k(total, [correct], k_value)[0]

    print("Results:")
    for k, v in pass_at_k.items():
        print(f"{k}: {v:.4f}")

    return pass_at_k
