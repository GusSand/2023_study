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

def evaluate_functional_correctness(
    sample_file: str,
    k: List[int] = [1, 10, 100],
    timeout: float = 20.0,
    problem_file: str = HUMAN_EVAL,
):
    problems = read_problems()
    results = []

    for sample in tqdm.tqdm(stream_yaml(sample_file)):
        task_id = sample["task_id"]
        completion = sample["completion"]
        result = unsafe_execute(problems[task_id], completion, timeout)
        results.append({
            "task_id": task_id,
            "completion": sample["completion"],
            "passed": result["passed"],
            "result": result["result"],
            "execution_time": result.get("execution_time", None)
        })

    # Write results to YAML file
    out_file = f"{sample_file}_results.yaml"
    with open(out_file, 'w') as f:
        yaml.dump(results, f)

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
