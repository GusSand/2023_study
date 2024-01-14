from transformers import AutoTokenizer
import transformers
import torch
import time

tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")

pipeline = transformers.pipeline(
    "text-generation",
    model="codellama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)

def main():
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

    for _ in range(10):
        main()