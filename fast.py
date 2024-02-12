from fastapi import FastAPI, HTTPException, Depends, Security, Header
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader, APIKey 
from typing import Optional
from dotenv import load_dotenv
import os
from transformers import AutoTokenizer
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import LlamaForCausalLM, CodeLlamaTokenizer
from vllm import LLM, SamplingParams

torch.set_default_device("cuda")

# tokenizer = CodeLlamaTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
# model  = LlamaForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf").to("cuda")
# pipeline = transformers.pipeline(
#     "text-generation",
#     model="codellama/CodeLlama-7b-hf",
#     torch_dtype=torch.float16,
#     device_map="auto",
# )


# tokenizer_llama34 = AutoTokenizer.from_pretrained("codellama/CodeLlama-34b-hf")
# model_llama34 = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-34b-hf").to("cuda")

tokenizer_phi2 = AutoTokenizer.from_pretrained("microsoft/phi-2")
model_phi2 = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")
#tokenizer_phi2 = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
#model_phi2 =  AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", trust_remote_code=True)

# starcoder =  "bigcode/starcoder"
# tokenizer_starcoder = AutoTokenizer.from_pretrained(starcoder)
# model_starcoder = AutoModelForCausalLM.from_pretrained(starcoder)

#load environment variables 
load_dotenv()
app = FastAPI()

API_KEY_NAME = "access_token"
#API_KEY = os.getenv("API_KEY")
API_KEY = "BAD_F00D"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class Prompt(BaseModel):
    text: str


def process_llama_7b(prompt_data):

    #inputs = tokenizer(prompt_data, return_tensors="pt", return_attention_mask=False)

    sequences = pipeline(
        prompt_data,
        #inputs.input_ids.to("cuda"),
        do_sample=True,
        temperature=0.1,
        top_p=0.95,
        num_return_sequences=1,
        return_full_text=False,
        eos_token_id=tokenizer.eos_token_id,
        max_length=100,
    )

    result = sequences[0]['generated_text']

    # outputs = model.generate(inputs['input_ids'].to("cuda"), 
    #                               max_length=100, 
    #                               do_sample=True, 
    #                               top_p=0.95, 
    #                               top_k=60, 
    #                               return_full_text=False, 
    #                               num_return_sequences=1)
    # generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # return generated_text
    return result    

def process_llama_34b(prompt_data):

    inputs = tokenizer_llama34.encode(prompt_data, return_tensors="pt", return_attention_mask=False)
    outputs = model_llama34.generate(inputs, 
                                  max_length=100, 
                                  do_sample=True, 
                                  top_p=0.95, 
                                  top_k=60, 
                                  num_return_sequences=1)
    
    generated_text = tokenizer_llama34.decode(outputs[0], skip_special_tokens=True)
    return generated_text


def process_phi2(prompt_data):

    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
    llm = LLM(model="facebook/opt-125m")
    outputs = llm.generate(prompts, sampling_params)

    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")



    # try:
    #     from vllm import LLM, SamplingParams
            
    #     llm = LLM(model="microsoft/phi-2")
    #     # Create a sampling params object.
    #     sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
    #     outputs = llm.generate(prompt_data, sampling_params, tensor_parallel_size=0)
    #     generated_text = outputs[0].text
    #     return generated_text


    # except Exception as e:
    #     print(e)
    #     return "Error: " + str(e)

def process_phi2_old(prompt_data):

    inputs = tokenizer_phi2.encode(prompt_data, return_tensors="pt", return_attention_mask=False)    
    outputs = model_phi2.generate(inputs, max_length=200)
    generated_text = tokenizer_phi2.batch_decode(outputs)[0]
    #print(generated_text)
    return generated_text
    # inputs = tokenizer_phi2.encode(prompt_data, return_tensors="pt", return_attention_mask=False)
    # outputs = model_phi2.generate(inputs, 
    #                               max_length=100, 
    #                               do_sample=True, 
    #                               top_p=0.95, 
    #                               top_k=60, 
    #                               num_return_sequences=1)
    
    # generated_text = tokenizer_phi2.decode(outputs[0], skip_special_tokens=True)
    # return generated_text


def process_starcoder(prompt_data):

    input = tokenizer_starcoder.encode(prompt_data, return_tensors="pt", return_attention_mask=False)
    outputs = model_starcoder.generate(input, 
                                  max_length=100, 
                                  do_sample=True, 
                                  top_p=0.95, 
                                  top_k=60, 
                                  num_return_sequences=1)
    generated_text = tokenizer_starcoder.decode(outputs[0], skip_special_tokens=True)
    return generated_text


model_functions = {
    "llama_7b": process_llama_7b,
    "llama_34b": process_llama_34b,
    "phi2": process_phi2,
    "starcoder": process_starcoder,
}

@app.post("/process_prompt")
async def process_prompt(prompt_data: dict, authorization: str = Header(None)):

    try:
        # Check the authorization header for the access token
        expected_api_key = "BAD_F00D"
        # if authorization != f"Bearer {expected_api_key}":
        #     raise HTTPException(status_code=401, detail="Unauthorized")
        
        if "model" not in prompt_data:
            raise HTTPException(status_code=400, detail="Missing model parameter")

        # Extract data from the JSON request
        model = prompt_data.get("model")

        if model not in model_functions:
            model = "llama_7b"
        
        prompt = prompt_data.get("prompt")
        
        if prompt is None:
            raise HTTPException(status_code=400, detail="Missing prompt parameter")
        
        max_tokens = prompt_data.get("max_tokens", 100)


        # Call the appropriate Python function based on the model
        the_response = model_functions[model](prompt)

        # Perform processing using the received data (replace this with your actual logic)
        result = {
            "model": model,
            #"prompt": prompt,
            "max_tokens": max_tokens,
            "response": the_response # Replace with your actual response
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
