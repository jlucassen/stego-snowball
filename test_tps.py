import transformers
import torch
from time import perf_counter
import dotenv
import os
from tqdm import tqdm

from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer

dotenv.load_dotenv()
messages = [[{"role": "user", "content": "Count to 10."}]]*5
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

uq = q8 = AutoModelForCausalLM.from_pretrained(
    model_id, 
    quantization_config=BitsAndBytesConfig()
)

q8 = AutoModelForCausalLM.from_pretrained(
    model_id, 
    quantization_config=BitsAndBytesConfig(load_in_8bit=True)
)

q4 = AutoModelForCausalLM.from_pretrained(
    model_id, 
    quantization_config=BitsAndBytesConfig(load_in_8bit=True)
)

q4plus = AutoModelForCausalLM.from_pretrained(
    model_id, 
    quantization_config=BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
    )
)



def test_model(model):
    pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    tokenizer = AutoTokenizer.from_pretrained(model_id),
    token=os.getenv('HF_TOKEN')
    )
    
    terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    token_total = 0

    t1_start = perf_counter() 
    for _ in tqdm(list(range(5))):
        outputs = pipeline(
            messages,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            pad_token_id=pipeline.tokenizer.eos_token_id
        )
        print(outputs)
        token_total += sum([len(output[0]["generated_text"][-1]['content']) for output in outputs])
    t1_stop = perf_counter()
    return token_total, t1_stop-t1_start, token_total/(t1_stop-t1_start)

print(f"uq: {test_model(uq)}")
print(f"q8: {test_model(q8)}")
print(f"q4: {test_model(q4)}")
print(f"q4plus: {test_model(q4plus)}")