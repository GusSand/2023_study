from fastapi import FastAPI, HTTPException, Depends, Security, Header
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader, APIKey 
from typing import Optional
from dotenv import load_dotenv
import os
from transformers import AutoTokenizer
import transformers
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer


transfomers_token = "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"

tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")


pipeline = transformers.pipeline(
    "text-generation",
    model="codellama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)

tokenizer_phi2 = AutoTokenizer.from_pretrained("microsoft/phi-2")
model_phi2 = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")

starcoder =  "bigcode/starcoder"
tokenizer_starcoder = AutoTokenizer.from_pretrained(starcoder)
model_starcoder = AutoModelForCausalLM.from_pretrained(starcoder).to("cuda")

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

    sequences = pipeline(
        prompt_data,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=100,
    )

    return sequences[0]['generated_text']
    

def process_phi2(prompt_data):

    inputs = tokenizer_phi2.encode(prompt_data, return_tensors="pt", return_attention_mask=False)
    outputs = model_phi2.generate(inputs, 
                                  max_length=100, 
                                  do_sample=True, 
                                  top_p=0.95, 
                                  top_k=60, 
                                  num_return_sequences=1)
    
    generated_text = tokenizer_phi2.decode(outputs[0], skip_special_tokens=True)
    return generated_text


def process_starcoder(prompt_data):

    input = tokenizer_starcoder.encode(prompt_data, return_tensors="pt", return_attention_mask=False).to("cuda")
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
    "phi2": process_phi2,
    "starcoder": process_starcoder,
}

@app.post("/process_prompt/")
async def process_prompt(prompt_data: dict, authorization: str = Header(None)):

    try:
        # Check the authorization header for the access token
        expected_api_key = "BAD_F00D"
        if authorization != f"Bearer {expected_api_key}":
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        if "model" not in prompt_data:
            raise HTTPException(status_code=400, detail="Missing model parameter")

        # Extract data from the JSON request
        model = prompt_data.get("model")

        if model not in model_functions:
            raise HTTPException(status_code=400, detail="Invalid model parameter")
        
        prompt = prompt_data.get("prompt")
        
        if prompt is None:
            raise HTTPException(status_code=400, detail="Missing prompt parameter")
        
        max_tokens = prompt_data.get("max_tokens", 100)


        # Call the appropriate Python function based on the model
        the_response = model_functions[model](prompt)

        # Perform processing using the received data (replace this with your actual logic)
        result = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "response": the_response # Replace with your actual response
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
