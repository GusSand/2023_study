import requests
import json
import torch
import time

# Set your OpenAI API key
api_key = ""
api_llama = "BAD_F00D"

# Set the API endpoint URL for OpenAI GPT-3.5-turbo
url = "https://api.openai.com/v1/completions"
url_llama = "http://localhost:8000/process_prompt"

# Prepare headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_llama}"
}

# Prepare the data to be sent in the POST request
# This is where you set your prompt and other parameters
#    "prompt": "The code for a basic Python function that adds two numbers is:", # Your prompt here

prompt = "# Print all primes between 1 and n \n def print_primes(n):"
data = {

    #"model": "gpt-3.5-turbo-instruct",  # Codex model for code-related tasks
    "model": "phi2",  # Codex model for code-related tasks
    #"model": "llama_7b",  # Codex model for code-related tasks
    #"model": "starcoder",  # Codex model for code-related tasks
    "prompt": prompt, 
    "max_tokens": 100, 
}

# if torch.cuda.is_available():
# #   torch.set_default_tensor_type(torch.cuda.HalfTensor)
#     print("cuda!!")
# elif torch.backends.mps.is_available():
#     mps_device = torch.device("mps")
#     x = torch.ones(1, device=mps_device)
#     print(x)
# else:
#     print("Nope")


print("Sending the request...")
print("model:", data["model"])

# Send the POST request
st = time.time()
response = requests.post(url_llama, headers=headers, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Parse and print the response
    print(json.dumps(response.json(), indent=4))
else:
    # Print error message
    print("Error:", response.status_code, response.text)

#get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')