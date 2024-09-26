from typing import Iterable, Dict
from yaml_loader import load_yaml_tests
import gzip
import json
import os
import yaml


ROOT = os.path.dirname(os.path.abspath(__file__))
HUMAN_EVAL_YAML = "eval.yaml"


def read_problems(evalset_file: str = HUMAN_EVAL_YAML):
    with open(evalset_file, 'r') as f:
        problems = yaml.safe_load(f)
    return {problem['task_id']: problem for problem in problems}


def stream_yaml(filename: str) -> Iterable[Dict]:
    """
    Reads a YAML file and yields each document as a dictionary
    """
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
        if isinstance(data, list):
            for item in data:
                yield item
        elif isinstance(data, dict):
            yield data
        else:
            raise ValueError("Unexpected YAML structure. Expected a list or a dictionary.")

def write_yaml(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to YAML
    """
    mode = 'a' if append else 'w'
    with open(filename, mode) as f:
        yaml.dump_all(data, f)
