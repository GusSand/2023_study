from openai import OpenAI

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://184.105.3.216:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

completion = client.completions.create(model="bigcode/starcoder",
                                      prompt="# Print all primes between 1 and n \n def print_primes(n):")

print('Starcoder: \n')
print("Completion result:", completion.choices[0].text)

# completion = client.completions.create(model="meta-llama/Llama-2-13b-hf",
#                                       prompt="# Print all primes between 1 and n \n def print_primes(n):")



# completion = client.completions.create(model="microsoft/phi-2",
#                                         prompt="# Print all primes between 1 and n \n def print_primes(n):")
# print('Phi-2: \n')
# print("Completion result:", completion.choices[0].text)