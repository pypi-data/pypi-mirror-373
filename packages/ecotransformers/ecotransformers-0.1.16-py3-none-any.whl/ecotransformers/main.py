import torch  
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import time
import numpy as np
import evaluate
import gc
import argparse

torch.manual_seed(42)
np.random.seed(42)

model = None
tokenizer = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

perplexity_metric = evaluate.load("perplexity", module_type="metric")
bleu_metric = evaluate.load("bleu")
rouge_metric = evaluate.load("rouge")

frozen_layers = {}
frozen_layer_names = []

def load_model(model_name):
    global model, tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()
    return model, tokenizer

def freeze_hook(module, input, output, layer_name):
    frozen_output = torch.where(torch.abs(output) < 1e-12,
                                torch.zeros_like(output), output)
    frozen_layers[layer_name] = frozen_output.detach()
    return frozen_output

def apply_freeze_hooks(model):
    for name, module in model.named_modules():
        if "mlp" in name and hasattr(module, "forward"):
            module.register_forward_hook(
                lambda mod, inp, out, n=name: freeze_hook(mod, inp, out, n)
            )
            frozen_layer_names.append(name)
    print(f"Total layers registered for self-freezing: {len(frozen_layer_names)}")

def self_prune(model, threshold=1e-12):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if "weight" in name and len(param.shape) > 1:
                mask = param.abs() > threshold
                param.mul_(mask.float())

def free_gpu_memory():
    torch.cuda.empty_cache()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()

prompt_cache = {}

def cached_infer(prompt, model_name):
    if model is None or tokenizer is None:
        raise ValueError("Model not loaded. Please call load_model(model_name) first.")

    if prompt in prompt_cache:
        return prompt_cache[prompt]

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50, do_sample=False)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    prompt_cache[prompt] = result
    return result

def evaluate_model(prompt, reference, model_name):
    generated = cached_infer(prompt, model_name)
    return generated  # Only return generated text

def transformer(model_name, prompt, reference):
    free_gpu_memory()
    load_model(model_name)

    # Apply optimization techniques
    self_prune(model, threshold=1e-12)
    apply_freeze_hooks(model)

    # Track only optimized inference
    tracker_optimized = EmissionsTracker(project_name="optimized", save_to_file=False)
    tracker_optimized.start()
    start_opt = time.time()
    output_optimized = evaluate_model(prompt, reference, model_name)
    end_opt = time.time()
    optimized_emissions = tracker_optimized.stop()
    optimized_time = end_opt - start_opt

    # Return optimized text and metrics
    return output_optimized, optimized_time, optimized_emissions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True,
                        help="Any Hugging Face causal LM model (e.g., EleutherAI/gpt-neo-1.3B)")
    parser.add_argument("--prompt", type=str, required=True,
                        help="Prompt for text generation")
    parser.add_argument("--reference", type=str, required=True,
                        help="Reference text for evaluation")
    args = parser.parse_args()

    text, opt_time, opt_co2 = transformer(args.model, args.prompt, args.reference)

    # Print only optimized tracking results
    print("\n=== OPTIMIZATION GAINS ===")
    print(f"Inference Time: {opt_time:.2f}s")
    print(f"CO2 Emissions: {opt_co2:.6f} kg")

    return text  # Only return optimized generated text

if __name__ == "__main__":
    main()
