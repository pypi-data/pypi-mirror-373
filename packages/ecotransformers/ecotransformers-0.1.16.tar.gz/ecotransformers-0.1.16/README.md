# 🌱 AI Transformer Optimizer with CO₂ Tracking

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Transformers](https://img.shields.io/badge/Transformers-HuggingFace-orange)](https://huggingface.co/docs/transformers/index)
[![CodeCarbon](https://img.shields.io/badge/CO₂-Tracked-green)](https://mlco2.github.io/codecarbon/)

This package provides an **easy wrapper for Transformer-based models** with:
- ✅ **Baseline vs Optimized inference** comparison  
- ✅ **Self-pruning** (removing near-zero weights)  
- ✅ **Self-freezing** (zeroing inactive activations)  
- ✅ **Perplexity, BLEU, ROUGE metrics**  
- ✅ **CO₂ emissions tracking** (powered by [CodeCarbon](https://mlco2.github.io/codecarbon/))  

---

## 📦 Installation

Clone this repo and install dependencies:

```bash
git clone https://github.com/yourusername/transformer-optimizer.git
cd transformer-optimizer
pip install -r requirements.txt
