# CosyVoice2-EU

<div align="center">
  <img src="https://horstmann.tech/cosyvoice2-demo/cosyvoice2-logo-clear.png" alt="CosyVoice2-EU Logo" width="400"/>
</div>

Minimal, plug-and-play CosyVoice2 European inference CLI that downloads our model from Hugging Face and runs cross-lingual zero-shot voice cloning TTS. It bundles the required `cosyvoice` runtime and `matcha` module so you don't need the full upstream repo.

Currently supports French and German, with more European languages coming soon!


## Quick Start

1. **Install the package:**
   ```bash
   pip install cosyvoice2-eu
   ```

2. **Run French voice cloning:**
   ```bash
   cosy2-eu \
     --text "Bonjour, je travaille dans une entreprise de technologie à Paris. CosyVoice 2 offre des capacités de synthèse vocale remarquables." \
     --prompt french_speaker.wav \
     --out output_french.wav
   ```

3. **Run German voice cloning:**
   ```bash
   cosy2-eu \
     --text "Guten Tag, ich arbeite in einem Technologieunternehmen in Berlin. CosyVoice 2 bietet beeindruckende Sprachsynthese-Funktionen." \
     --prompt german_speaker.wav \
     --out output_german.wav
   ```

That's it! The first run will automatically download the model from Hugging Face.


## 🎯 Features

- **Easy Installation**: Simple `pip install cosyvoice2-eu` command
- **Cross-lingual Voice Cloning**: Clone voices across different European languages
- **French & German Support**: Supports French and German text-to-speech with voice cloning
- **More Languages Coming**: Additional European language support in development
- **Bundled Runtime**: No need to install the full upstream CosyVoice2 repository
- **Hugging Face Integration**: Automatic model downloading from [Hugging Face](https://huggingface.co/Luka512/CosyVoice2-0.5B-EU)
- **Multiple LLM Backbones**: Support for different language model backbones (see below)

## 🚀 Upcoming Features

**Multiple LLM Backbone Support** - Code is ready, models are currently training:
- **Qwen3 0.6B**: Lightweight model for efficient inference
- **EuroLLM 1.7B Instruct**: Specialized European language model
- **Mistral 7B v0.3**: Powerful multilingual capabilities

*Currently ships with the original CosyVoice2 "blankEN" backbone and our fine-tuned LM and flow models. New backbones will be available as separate model downloads once training is complete.*

## 📖 Model & Credits

This package uses our **CosyVoice2-0.5B-EU** model available at: 
🤗 [Luka512/CosyVoice2-0.5B-EU](https://huggingface.co/Luka512/CosyVoice2-0.5B-EU)

**Built on CosyVoice2**: This project is based on the excellent [CosyVoice2](https://github.com/FunAudioLLM/CosyVoice2) by FunAudioLLM, adapted for European language support with cross-lingual voice cloning capabilities.

## 📜 License

This project is licensed under the Apache License 2.0. 

**Note**: This package includes code from:
- [CosyVoice2](https://github.com/FunAudioLLM/CosyVoice2) (Apache 2.0) - Original TTS framework
- [Matcha-TTS](https://github.com/shivammathur/Matcha-TTS) (Apache 2.0) - Neural vocoder components

All original licenses and attributions are preserved.

## Installation

### From PyPI (Recommended)

```bash
pip install cosyvoice2-eu
```

### For enhanced English phonemization (optional):
```bash
pip install cosyvoice2-eu[piper]
```

**Note**: The `piper` optional dependency requires compilation tools and may fail in some environments (like Google Colab). The package will work without it, using the standard phonemizer as fallback.

If you are on Linux with GPU, ensure you install torch/torchaudio matching your CUDA and have `onnxruntime-gpu` available. If CPU-only, `onnxruntime` will be sufficient.

### Development Installation

```bash
cd standalone_infer
pip install -e .
```

## Usage

**French Example:**
```bash
cosy2-eu \
  --text "Bonjour, je travaille dans une entreprise de technologie à Paris. CosyVoice 2 offre des capacités de synthèse vocale remarquables." \
  --prompt french_speaker.wav \
  --out output_french.wav
```

**German Example:**
```bash
cosy2-eu \
  --text "Guten Tag, ich arbeite in einem Technologieunternehmen in Berlin. CosyVoice 2 bietet beeindruckende Sprachsynthese-Funktionen." \
  --prompt german_speaker.wav \
  --out output_german.wav
```

First run will download the model assets to `~/.cache/cosyvoice2-eu` (configurable via `--model-dir`).

**Advanced options:** `--setting`, `--llm-run-id`, `--flow-run-id`, `--hifigan-run-id`, `--final`, `--stream`, `--speed`, `--no-text-frontend`, `--backbone`, `--repo-id`, `--no-hf`.




