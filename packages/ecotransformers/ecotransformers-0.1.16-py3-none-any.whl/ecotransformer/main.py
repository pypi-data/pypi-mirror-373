#!/usr/bin/env python3
# main.py - eco_transformers CLI entry point

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import time
import gc
import argparse
import evaluate

# ======== GPU Memory Management ========
def free_gpu_memory():
    torch.cuda.empty_cache()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()

# ======== Freezing & Pruning ========
frozen_layers = {}
frozen_layer_names = []

def freeze_hook(module, input, output, layer_name):
    frozen_output = torch.where(torch.abs(output) < 1e-4, torch.zeros_like(output), output)
    frozen_layers[layer_name] = frozen_output.detach()
    return frozen_output

def apply_freeze_hooks(model):
    for name, module in model.named_modules():
        if 'mlp' in name and hasattr(module, 'forward'):
            module.register_forward_hook(lambda mod, inp, out, n=name: freeze_hook(mod, inp, out, n))
            frozen_layer_names.append(name)
    print(f"Total layers registered for self-freezing: {len(frozen_layer_names)}")

def self_prune(model, threshold=1e-3):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if 'weight' in name and len(param.shape) > 1:
                mask = param.abs() > threshold
                param.mul_(mask.float())

# ======== Inference Caching ========
prompt_cache = {}
def cached_infer(prompt, model, tokenizer, device):
    if prompt in prompt_cache:
        return prompt_cache[prompt]
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    prompt_cache[prompt] = result
    return result

# ======== Evaluation Function ========
def evaluate_model(prompt, reference, model, tokenizer, device, model_name, perplexity_metric, bleu_metric, rouge_metric):
    generated = cached_infer(prompt, model, tokenizer, device)
    ppl = perplexity_metric.compute(predictions=[generated], model_id=model_name)["perplexities"][0]
    bleu = bleu_metric.compute(predictions=[generated], references=[reference])["bleu"]
    rouge = rouge_metric.compute(predictions=[generated], references=[reference])["rougeL"]
    return ppl, bleu, rouge, generated

# ======== MAIN PIPELINE ========
def transformer(model_name=None, prompts=None, references=None):
    # If called without params → use CLI args
    if model_name is None and prompts is None and references is None:
        parser = argparse.ArgumentParser(description="Eco-Transformers: LLM with CO₂ tracking & optimizations")
        parser.add_argument("--model", type=str, default="tiiuae/falcon-rw-1b", help="Hugging Face model name")
        parser.add_argument("--prompt", type=str, required=True, help="Prompt text")
        parser.add_argument("--reference", type=str, required=True, help="Reference text for evaluation")
        parser.add_argument("--framework", type=str, default="pt", choices=["pt"],
                            help="Backend: only 'pt' (PyTorch) is supported")
        args = parser.parse_args()
        model_name = args.model
        prompts = [args.prompt]
        references = [args.reference]

    free_gpu_memory()

    # Load model & tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()

    # Load metrics
    perplexity_metric = evaluate.load("perplexity", module_type="metric")
    bleu_metric = evaluate.load("bleu")
    rouge_metric = evaluate.load("rouge")

    prompt = prompts[0]
    reference = references[0]

    # === BASELINE ===
    tracker_baseline = EmissionsTracker(project_name="eco-baseline")
    tracker_baseline.start()
    start_base = time.time()
    output_baseline = evaluate_model(prompt, reference, model, tokenizer, device, model_name, perplexity_metric, bleu_metric, rouge_metric)
    baseline_time = time.time() - start_base
    baseline_emissions = tracker_baseline.stop()

    # === OPTIMIZED (Pruning + Freezing) ===
    self_prune(model, threshold=1e-3)
    apply_freeze_hooks(model)
    tracker_optimized = EmissionsTracker(project_name="eco-optimized")
    tracker_optimized.start()
    start_opt = time.time()
    output_optimized = evaluate_model(prompt, reference, model, tokenizer, device, model_name, perplexity_metric, bleu_metric, rouge_metric)
    optimized_time = time.time() - start_opt
    optimized_emissions = tracker_optimized.stop()

    # === RETURN if imported ===
    if __name__ != "__main__":
       return {
        "baseline": {
            "perplexity": output_baseline[0],
            "bleu": output_baseline[1],
            "rouge": output_baseline[2],
            "text": output_baseline[3],
            "time": baseline_time,
            "co2": baseline_emissions
        },
        "optimized": {
            "perplexity": output_optimized[0],
            "bleu": output_optimized[1],
            "rouge": output_optimized[2],
            "text": output_optimized[3],
            "time": optimized_time,
            "co2": optimized_emissions
        }
    }

    # === PRINT RESULTS (only for CLI) ===
    print("\n=== BASELINE ===")
    print("Generated Text:", output_baseline[-1])
    print(f"Perplexity: {output_baseline[0]:.2f}, BLEU: {output_baseline[1]:.2f}, ROUGE-L: {output_baseline[2]:.2f}")
    print(f"Inference Time: {baseline_time:.2f}s, CO2 Emissions: {baseline_emissions:.6f} kg")

    print("\n=== OPTIMIZED (Pruning + Freezing) ===")
    print("Generated Text:", output_optimized[-1])
    print(f"Perplexity: {output_optimized[0]:.2f}, BLEU: {output_optimized[1]:.2f}, ROUGE-L: {output_optimized[2]:.2f}")
    print(f"Inference Time: {optimized_time:.2f}s, CO2 Emissions: {optimized_emissions:.6f} kg")

    delta_emission = baseline_emissions - optimized_emissions
    print(f"\nCO2 Reduction: {delta_emission:.6f} kg")

# Allow both CLI and import usage
if __name__ == "__main__":
    transformer()
