# %%
import transformers
import torch
from time import perf_counter

# %%
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    token="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"
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

token_total = 0
t1_start = perf_counter() 
for _ in range(100):
    outputs = pipeline(
        messages,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=pipeline.tokenizer.eos_token_id
    )
    token_total += len(outputs[0]["generated_text"][-1]['content'])
t1_stop = perf_counter()
print(f"Got {token_total} tokens in {t1_stop-t1_start} seconds, {token_total/(t1_stop-t1_start)} tokens per second.")
# %%
