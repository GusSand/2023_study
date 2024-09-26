import sys
import os
import openai
import subprocess
import time
from transformers import GPT2TokenizerFast
import fire
import tempfile

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

engine_tokens = {
    'code-davinci-001': 4080,
    'code-davinci-002': 4080,
    'code-cushman-001': 2030,
}

BASENAME = os.path.dirname(os.path.realpath(__file__))
DEFAULT_KEY_PATH = os.path.join(BASENAME, 'openai.key')
RATE_LIMIT_WAIT = 30

class PythonCodeGenerator:
    def __init__(self,
                 engine='code-davinci-002',
                 temperature=0.6,
                 key=DEFAULT_KEY_PATH,
                 num_solutions=1,
                 attempts_per_function=10,
                 output_prefix='gen_python',
                 dir='student_version'):
        self.engine = engine
        self.temperature = temperature
        self.key = key
        self.num_solutions = num_solutions
        self.attempts_per_function = attempts_per_function
        self.output_prefix = output_prefix
        self.dir = dir

        # Set up OpenAI API
        openai.api_key_path = self.key
        
        # Set up tokenizer
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

        self.MAX_TOKENS = engine_tokens[self.engine] - 512  # Reserve some tokens for the completion

    def try_run_python(self, source):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(source)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['python3', temp_file_path], capture_output=True, text=True, timeout=5)
            os.unlink(temp_file_path)
            if result.returncode != 0:
                print("Execution failed:")
                print(result.stderr)
                return False
            return True
        except subprocess.TimeoutExpired:
            print("Execution timed out")
            os.unlink(temp_file_path)
            return False

    def get_completion(self, prompt):
        while True:
            try:
                response = openai.Completion.create(
                    engine=self.engine,
                    echo=False,
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=512,
                    top_p=1.0,
                    stop=["\n\n", "```"],
                    n=1,
                )
                break
            except openai.error.RateLimitError as e:
                print(f"Rate limit exceeded ({e}), waiting {RATE_LIMIT_WAIT} seconds")
                time.sleep(RATE_LIMIT_WAIT)
        return response.choices[0].text.strip()

    def generate_python_code(self):
        base_file = os.path.join(self.dir, 'base_script.py')
        with open(base_file, 'r') as f:
            base_content = f.read()

        for i in range(self.num_solutions):
            print(f"====> Generating solution {i}")
            output_filename = f'{self.output_prefix}_{self.engine}_{i:02d}.py'
            
            prompt = f"{base_content}\n# Complete the following Python code:\n"
            full_code = base_content

            while "# TODO:" in full_code:
                prompt = self.tokenizer.decode(self.tokenizer.encode(prompt)[-self.MAX_TOKENS:])
                completion = self.get_completion(prompt)
                full_code = full_code.replace("# TODO:", completion, 1)
                prompt = full_code + "\n# Complete the following Python code:\n"

            print("Attempting to run generated Python code:")
            print(full_code)

            if self.try_run_python(full_code):
                print(f"Successfully generated a working Python script")
                with open(output_filename, 'w') as f:
                    f.write(full_code)
                print(f"Saved solution {i} to {output_filename}")
            else:
                print(f"Failed to generate a working Python script")

    def run(self):
        self.generate_python_code()

if __name__ == '__main__':
    fire.Fire(PythonCodeGenerator)