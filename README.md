# BitLinear


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

I just did not come up with some better naming, lol.

This repository contains my experimental package where I: - Were
inspired by [“The Era of 1-bit LLMs: All Large Language Models are in
1.58 Bits”](https://arxiv.org/abs/2402.17764) approach

- Essentially guys have proven that $log_2(3)$ bits of *informational
  capacity* per parameter is enought to pretrain a language model (they
  have shown that we can make a linear layer operating *factual* weights
  having only three values $(-scale, 0, scale)$).

- However since they used, well, fully-gradiental method to train LLM -
  in the reality weights were 16/32 bit, and were quantized to these
  values on the fly by some (approximately) differentiable quantization
  function

- By the way it also means that if model have $|W|$ trainable weights -
  optimizing through an optimizer like Adam will consume
  $3|W|dataTypeBytes$ parameters

- On the other hand in [“ReLoRA: High-Rank Training Through Low-Rank
  Updates”](https://arxiv.org/abs/2307.05695) other researchers show
  that if we freeze the original model and do incremental procedure of
  “train LoRA adapters - merge them into the original model - reset
  optimizer state” - the quality becomes comparable with standart
  training approach

  - So the gradient updates do not apply to the original model weights
    here, means we:

    - Need only $3(|A|+|B|)dataTypeBytes + |W|dataTypeBytes$ bytes of
      memory used by the optimization process (where $|A|$ and $|B|$ is
      an summary amount of parameters in $LoraA$ / $LoraB$ accross the
      whole model)

    - However the original model need to be stored in memory fully

So I made a custom linear layer which:

- Do not store original weights for long - only save to file, quantize
  it and than store quantized weights inside itself (so each byte
  represents a group of 5 parameters)

  - So \$ W\_{quant} = quantize(W) \$

- Do dequantization during a forward pass and adds adapter as well

  - \$ dequantize(W\_{quant}) x + bias + LoRA(x) \$

- Can merge LoRA adapter inside itself

  - To do so it:

    - Load the file with a previously saved weights

    - Merge LoRA’s $\Delta W$: \$ W = W + W \$

    - Save these new weights

    - Quantize it \$ W\_{quant} = quantize(W) \$

  - Surely with such a procedure we *must* except some quality loss:

    - At first - LoRA were trained to work upon quantized weights, which
      is a mere approximation of the original ones

    - At second - LoRA-introduced update than becomes quantized again

And ReLoRA training is basically the same as in the corresponding paper
(except for the way we merge model and LoRA’s).

Now I am conducting experiments to see how well does the approach works.

## Install

``` sh
pip install bitlinear@git+https://github.com/alex4321/bitlinear.git
```

## Experiment results

- Pretraining

I conducted two experiments [raw Mistral architecture model
pretraining](experiments/00_pretraining/mistral-training.ipynb) and
[BitNet+ReLoRA Mistral architecture model
pretraining](experiments/00_pretraining/bitmistral-training-lr-2e-4-rank-128--2000-restart.ipynb)

and results end up being comparable.

For the original method I got

    Step    Training Loss   Validation Loss Memory Usage Mb
    2000    5.178500    4.655300    29107
    4000    4.267300    4.253386    29541
    6000    3.997500    4.030161    30021
    8000    4.739200    3.861828    30521
    10000   3.159500    3.761141    30521
    12000   4.065400    3.672445    30521
    14000   3.764200    3.598749    30521
    16000   3.897100    3.530349    30521
    18000   3.261500    3.468710    30521
    20000   2.736200    3.411213    30521
    22000   2.150800    3.359339    30521
    24000   2.949400    3.317924    30521

while for optimized one:

    Step    Training Loss   Validation Loss Memory Usage Mb
    2000    5.049300    4.500881    8928
    4000    4.113500    4.085669    8840
    6000    3.948200    3.910413    8636
    8000    4.600700    3.776079    10518
    10000   3.124400    3.722620    9386
    12000   4.122400    3.669651    8794
    14000   3.781300    3.606225    8486
    16000   3.858200    3.570461    8912
    18000   3.319800    3.529242    8826
    20000   2.763000    3.487872    9796
    22000   2.137100    3.442672    9616
    24000   3.097400    3.421924    8994
    -
    26000   2.706200    3.380465    9468
    28000   3.897200    3.357405    10138
    30000   3.217000    3.332875    9786

## How to use

Here I will make a simple example upon which I am experimenting now
(there is still some debugging)

``` python
import os
import datasets
from transformers import AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments, Trainer, \
    TrainerCallback
from transformers.models.mistral import MistralConfig
from bitlinear.adapters import LoRAAdapter
from bitlinear.models.mistral import BitMistralForCausalLM
from bitlinear.relora import ReLoRAOptimizer, ReLoRASchedulerLambda
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
import subprocess
import torch

import warnings
warnings.filterwarnings("ignore")

STORE_DIR = "StoredWeights"

os.makedirs(STORE_DIR, exist_ok=True)

config = MistralConfig(
    vocab_size=32000,
    hidden_size=4160, # Original Mistral have 4090, this is closest multiplier for both 5 and 32
    intermediate_size=14400, # Original Mistral have 14336, this is closest multiplier for both 5 and 32
    num_hidden_layers=5, # Instead of 32 - to make model roughly 1-billion params
    num_attention_heads=32,
    num_key_value_heads=8,
    hidden_act="silu",
    max_position_embeddings=32768,
    initializer_range=0.02,
    rms_norm_eps=1e-5,
    use_cache=True,
    rope_theta=10000.0,
    sliding_window=4096,
    attention_dropout=0.0,
)
model = BitMistralForCausalLM(
    config=config,
    fname_prefix=f"{STORE_DIR}/bitmistal"
).to("cuda:0")

model.add_adapters(
    LoRAAdapter,
    {
        "lora_rank": 128,
    }
)

optimizer = ReLoRAOptimizer(
    model.parameters(),
    model.mergeable_layers(),
    optimizer_cls=AdamW,
    optimizer_params={},
    reset_n_steps=500,
    lr=1e-5,
)
lr_scheduler = LambdaLR(
    optimizer,
    ReLoRASchedulerLambda(
        lr_lambda=lambda step: step / 1000 if step < 1000 else min(1.0 - (step - 50000) / 50000, 1e-5),
        warmup_n_steps=100,
        reset_n_steps=500,
    )
)

optimizer = ReLoRAOptimizer(
    model.parameters(),
    model.mergeable_layers(),
    optimizer_cls=AdamW,
    optimizer_params={},
    reset_n_steps=500,
    lr=1e-5,
)
lr_scheduler = LambdaLR(
    optimizer,
    ReLoRASchedulerLambda(
        lr_lambda=lambda step: step / 1000 if step < 1000 else min(1.0 - (step - 50000) / 50000, 1e-5),
        warmup_n_steps=100,
        reset_n_steps=500,
    )
)

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=1024)

# Tokenize all parts of the dataset
tokenized_datasets = dataset_text.map(tokenize_function, batched=True, remove_columns=["text"])
tokenized_datasets

data_collator = DataCollatorForLanguageModeling(tokenizer, 
                                                mlm=False,
                                                pad_to_multiple_of=8)

class GpuMemoryLoggingCallback(TrainerCallback):
    """A custom callback for logging GPU memory usage."""
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        # Check if CUDA is available to avoid errors on CPU-only environments
        if torch.cuda.is_available():
            # Assuming a single-GPU setup here; adjust for multi-GPU as needed
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,nounits,noheader'],
                                    capture_output=True, text=True)
            memory_usage = result.stdout.strip()
            
            # Convert memory usage to an integer (MB) and log it
            logs['gpu_memory_usage_mb'] = int(memory_usage)
        else:
            logs['gpu_memory_usage_mb'] = 0  # Default to 0 if not using GPU

model.train()
model.gradient_checkpointing_enable()
training_args = TrainingArguments(
    output_dir="./mistral-2b-stored-model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    per_device_eval_batch_size=4,
    eval_accumulation_steps=4,
    logging_dir="./mistral-2b-tensorboard-bitwise",
    logging_steps=1,
    save_strategy="steps",
    save_steps=2000,
    evaluation_strategy="steps",
    eval_steps=2000,
    fp16=True,
    gradient_checkpointing=True,
    report_to="tensorboard",
    max_steps=10000,
    # No need to specify data collator here, it's passed to the Trainer constructor
)

# Initialize the Trainer with the data collator
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],  # Assuming these are ready; dynamically tokenized if not
    eval_dataset=tokenized_datasets["validation"],
    data_collator=data_collator,
    optimizers=(optimizer, lr_scheduler),
    callbacks=[GpuMemoryLoggingCallback()],
)

# Train
trainer.train()
```

## TODO

- Make experiment with finetuning the existing model this way
- Make experiment with self-distillation from the existing model this
  way
- Write an optimized BitLinear kernel:
  - current one dequantize weights than feed them to
    `torch.nn.function.linear` so spawning dequantized weights in memory
    will take some time. Why not do matrix multiplication on the fly,
    this way further decrease an amount of memory required for both
    training and inference?
