from openai import OpenAI
import time 

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://184.105.3.216:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Send a request to the vLLM API server.
# The prompt is a Python function that prints all prime numbers between 1 and n.
# The model is vLLM's Starcoder model.

# time how long it takes to get a response
st = time.time()

completion = client.completions.create(model="bigcode/starcoder",
                                      prompt="# Print all primes between 1 and n \n def print_primes(n):")

print('Starcoder: \n')
print("Completion result:", completion)

for choice in completion.choices:
    print("Completion result:", choice.text)

t = time.time() - st
print("Time:", t)

# completion = client.completions.create(model="meta-llama/Llama-2-13b-hf",
#                                       prompt="# Print all primes between 1 and n \n def print_primes(n):")



# completion = client.completions.create(model="microsoft/phi-2",
#                                         prompt="# Print all primes between 1 and n \n def print_primes(n):")
# print('Phi-2: \n')
# print("Completion result:", completion.choices[0].text)