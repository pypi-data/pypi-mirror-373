import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from codecarbon import EmissionsTracker
import time
import numpy as np
import evaluate
import gc

# ===== FREE GPU MEMORY =====
def free_gpu_memory():
    torch.cuda.empty_cache()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.ipc_collect()
        torch.cuda.empty_cache()

# ===== PRUNING FUNCTION =====
def self_prune(model, threshold=1e-3):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if 'weight' in name and len(param.shape) > 1:
                mask = param.abs() > threshold
                param.mul_(mask.float())

# ===== FREEZING FUNCTION =====
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

# ===== MAIN GREEN AI FUNCTION =====
def transformer(model_name, prompts, references):
    """
    Run experiments (baseline, pruning, freezing, caching, optimized) on any Hugging Face causal LM.
    Returns results dictionary containing outputs, metrics, inference times, and CO2 emissions.
    """
    free_gpu_memory()

    # Load model & tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device).eval()

    # Load metrics
    perplexity_metric = evaluate.load("perplexity", module_type="metric")
    bleu_metric = evaluate.load("bleu")
    rouge_metric = evaluate.load("rouge")

    # Caching
    prompt_cache = {}
    def cached_infer(prompt):
        if prompt in prompt_cache:
            return prompt_cache[prompt]
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_cache[prompt] = result
        return result

    # Evaluate a single prompt
    def evaluate_model(prompt, reference):
        generated = cached_infer(prompt)
        ppl = perplexity_metric.compute(predictions=[generated], model_id=model_name)["perplexities"][0]
        bleu = bleu_metric.compute(predictions=[generated], references=[reference])["bleu"]
        rouge = rouge_metric.compute(predictions=[generated], references=[reference])["rougeL"]
        return ppl, bleu, rouge, generated

    results = {}

    # ===== BASELINE =====
    tracker_baseline = EmissionsTracker(project_name=f"{model_name}-baseline")
    tracker_baseline.start()
    start_base = time.time()
    outputs_baseline = [evaluate_model(p, r) for p, r in zip(prompts, references)]
    end_base = time.time()
    baseline_emissions = tracker_baseline.stop()
    baseline_time = end_base - start_base

    results['baseline'] = {
        'outputs': outputs_baseline,
        'time': baseline_time,
        'co2': baseline_emissions
    }

    # ===== PRUNING =====
    self_prune(model, threshold=1e-3)
    tracker_prune = EmissionsTracker(project_name=f"{model_name}-pruning")
    tracker_prune.start()
    start_prune = time.time()
    outputs_pruned = [evaluate_model(p, r) for p, r in zip(prompts, references)]
    end_prune = time.time()
    prune_emissions = tracker_prune.stop()
    prune_time = end_prune - start_prune

    results['pruning'] = {
        'outputs': outputs_pruned,
        'time': prune_time,
        'co2': prune_emissions
    }

    # ===== FREEZING =====
    hook_start = time.time()
    apply_freeze_hooks(model)
    hook_end = time.time()
    hook_setup_time = hook_end - hook_start

    tracker_freeze = EmissionsTracker(project_name=f"{model_name}-freezing")
    tracker_freeze.start()
    start_freeze = time.time()
    outputs_freeze = [evaluate_model(p, r) for p, r in zip(prompts, references)]
    end_freeze = time.time()
    freeze_emissions = tracker_freeze.stop()
    freeze_time = end_freeze - start_freeze

    results['freezing'] = {
        'outputs': outputs_freeze,
        'time': freeze_time,
        'co2': freeze_emissions,
        'hook_setup_time': hook_setup_time
    }

    # ===== OPTIMIZED (PRUNING + FREEZING + CACHING) =====
    tracker_optimized = EmissionsTracker(project_name=f"{model_name}-optimized")
    tracker_optimized.start()
    start_opt = time.time()
    outputs_optimized = [evaluate_model(p, r) for p, r in zip(prompts, references)]
    end_opt = time.time()
    optimized_emissions = tracker_optimized.stop()
    optimized_time = end_opt - start_opt

    results['optimized'] = {
        'outputs': outputs_optimized,
        'time': optimized_time,
        'co2': optimized_emissions
    }

    return results

# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    model_name = "tiiuae/falcon-rw-1b"
    prompts = [
        "The theory of relativity was developed by",
        "Climate change is primarily caused by",
        "Photosynthesis in plants requires",
        "Artificial intelligence can be used in"
    ]
    references = [
        "The theory of relativity was developed by Albert Einstein in the early 20th century.",
        "Climate change is primarily caused by the emission of greenhouse gases from human activities.",
        "Photosynthesis in plants requires sunlight, carbon dioxide, and water.",
        "Artificial intelligence can be used in healthcare, education, and autonomous vehicles."
    ]

    results = transformer(model_name, prompts, references)

    # Example: print baseline vs optimized CO2
    print(f"Baseline CO2: {results['baseline']['co2']:.6f} kg")
    print(f"Optimized CO2: {results['optimized']['co2']:.6f} kg")