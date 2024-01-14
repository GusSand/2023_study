from fastapi import FastAPI, HTTPException, Depends, Security
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


tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")


pipeline = transformers.pipeline(
    "text-generation",
    model="codellama/CodeLlama-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
)

tokenizer_phi2 = AutoTokenizer.from_pretrained("microsoft/phi-2")
model_phi2 = AutoModelForCausalLM.from_pretrained("microsoft/phi-2")

#load environment variables 
load_dotenv()
app = FastAPI()

API_KEY_NAME = "access_token"
#API_KEY = os.getenv("API_KEY")
API_KEY = "BAD_F00D"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class Prompt(BaseModel):
    text: str

async def get_api_key( api_key_header: Optional[str] = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
@app.post("/prompt_phi2/")
async def prompt_phi2(prompt: Prompt, api_key: APIKey = Depends(get_api_key)):

    try:
        response = process_prompt_phi2(prompt.text)
        return {"response":response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt_llama7b/")
async def prompt_llama7b(prompt: Prompt, api_key: APIKey = Depends(get_api_key)):

    try:
        response = process_prompt_llama7b(prompt.text)
        return {"response":response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def process_prompt_phi2(prompt):

    inputs = tokenizer_phi2.encode(prompt, return_tensors="pt", return_attention_mask=False)
    outputs = model_phi2.generate(inputs, 
                                  max_length=100, 
                                  do_sample=True, 
                                  top_p=0.95, 
                                  top_k=60, 
                                  num_return_sequences=1)
    
    generated_text = tokenizer_phi2.decode(outputs[0], skip_special_tokens=True)
    return generated_text


def process_prompt_llama7b(prompt):

        sequences = pipeline(
            prompt,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_length=100,
        )

        return sequences[0]['generated_text']
 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
