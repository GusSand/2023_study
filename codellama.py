from transformers import AutoTokenizer
import transformers
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")

pipeline = transformers.pipeline(
    "text-generation",
    model="codellama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)

def phi2():
    tokenizer_phi2 = AutoTokenizer.from_pretrained("microsoft/phi-2")
    model_phi2 = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")

    inputs = tokenizer('''def print_prime(n):
    """
    Print all primes between 1 and n
    """''', return_tensors="pt", return_attention_mask=False)

    outputs = model_phi2.generate(**inputs, max_length=200)
    text = tokenizer_phi2.batch_decode(outputs)[0]
    print(text)


def llama():
    st_begin = time.time()

    # repeat the process 10 times
    for i in range(10):
        st = time.time()

        sequences = pipeline(
            'def fibonacci(',
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_length=100,
        )

        for seq in sequences:
            print(f"Result: {seq['generated_text']}")

        #get the end time
        et = time.time()
        elapsed_time = et - st
        print('Total time:', elapsed_time, 'seconds')
        print('\n\n')

def check_cuda():
    if torch.cuda.is_available():
        print("cuda!!")
    elif torch.backends.mps.is_available():
        mps_device = torch.device("mps")
        x = torch.ones(1, device=mps_device)
        print("MPS")
    else:
        print("Nope")

if __name__ == "__main__":
    check_cuda()

    # for _ in range(10):
    #     llama()


    for _ in range(10):
        phi2()