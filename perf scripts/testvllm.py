from openai import OpenAI
<<<<<<< HEAD:testvllm.py
import time
=======
import time 
>>>>>>> fa6cab5f15ec8bb07972447f950234d3f62d5815:perf scripts/testvllm.py

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base_single = "http://184.105.3.216:8000/v1"
openai_api_base_multi = "http://184.105.5.97:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base_single,
)

<<<<<<< HEAD:testvllm.py
=======
# Send a request to the vLLM API server.
# The prompt is a Python function that prints all prime numbers between 1 and n.
# The model is vLLM's Starcoder model.
>>>>>>> fa6cab5f15ec8bb07972447f950234d3f62d5815:perf scripts/testvllm.py

# time how long it takes to get a response
st = time.time()

<<<<<<< HEAD:testvllm.py
#codellama/CodeLlama-34b-hf
#meta-llama/Llama-2-7b-hf
#codellama/CodeLlama-7b-Python-hf
completion = client.completions.create(model="meta-llama/Llama-2-7b-hf",
                                        max_tokens=100,
                                      prompt="# Print all primes between 1 and n \n def print_primes(n):")

#print('Starcoder: \n')
print("Completion result:", completion.choices[0].text)
print("Time:", time.time() - st)
=======
completion = client.completions.create(model="bigcode/starcoder",
                                      prompt="# Print all primes between 1 and n \n def print_primes(n):")

print('Starcoder: \n')
print("Completion result:", completion)

for choice in completion.choices:
    print("Completion result:", choice.text)

t = time.time() - st
print("Time:", t)
>>>>>>> fa6cab5f15ec8bb07972447f950234d3f62d5815:perf scripts/testvllm.py

# completion = client.completions.create(model="meta-llama/Llama-2-13b-hf",
#                                       prompt="# Print all primes between 1 and n \n def print_primes(n):")


# completion = client.completions.create(model="microsoft/phi-2",
#                                         max_tokens=100,          
#                                         prompt="# Print all primes between 1 and n \n def print_primes(n):")
# print('Phi-2: \n')
# print("Completion result:", completion.choices[0].text)

# t = time.time() - st
# print("Time:", t)