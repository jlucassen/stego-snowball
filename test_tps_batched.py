import transformers
import torch
from time import perf_counter
import dotenv
import os

dotenv.load_dotenv()

model_id = "meta-llama/Meta-Llama-3-70B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    token=os.getenv('HF_TOKEN')
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

def create_batch(messages, batch_size):
    return [messages for _ in range(batch_size)]

def process_batch(batch):
    outputs = pipeline(
        batch,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=pipeline.tokenizer.eos_token_id
    )
    return outputs

for batch_size in [1, 2, 4, 8]:
    num_batches = 10  # Total iterations will be batch_size * num_batches

    token_total = 0
    t1_start = perf_counter()

    for _ in range(num_batches):
        batch = create_batch(messages, batch_size)
        outputs = process_batch(batch)
        for output in outputs:
            token_total += len(output[0]["generated_text"][2]['content'])

    t1_stop = perf_counter()
    print(f"Batch size {batch_size}, got {token_total} tokens in {t1_stop-t1_start} seconds, {token_total/(t1_stop-t1_start)} tokens per second.")