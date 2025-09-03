import argparse
import os
import torchaudio

from huggingface_hub import snapshot_download

# Import the vendored runtime
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav


def main():
    parser = argparse.ArgumentParser(description='CosyVoice2 European Inference (cross-lingual cloning)')
    parser.add_argument('--text', type=str, required=True)
    parser.add_argument('--prompt', type=str, required=True, help='Path to a ≥16kHz prompt wav')
    parser.add_argument('--out', type=str, required=True)
    parser.add_argument('--model-dir', type=str, default=os.path.expanduser('~/.cache/cosyvoice2-eu'))
    parser.add_argument('--repo-id', type=str, default='Luka512/CosyVoice2-0.5B-EU', help='HF repo to auto-download into --model-dir unless --no-hf is set')
    parser.add_argument('--no-hf', action='store_true', help='Do not download from HF; assume --model-dir already exists')
    parser.add_argument('--setting', type=str, default='llm_flow_hifigan', help='original|llm|flow|hifigan|llm_flow|llm_hifigan|flow_hifigan|llm_flow_hifigan')
    parser.add_argument('--llm-run-id', type=str, default='latest')
    parser.add_argument('--flow-run-id', type=str, default='latest')
    parser.add_argument('--hifigan-run-id', type=str, default='latest')
    parser.add_argument('--final', action='store_true', help='Use final checkpoints (llm.pt/flow.pt/hift.pt)')
    parser.add_argument('--stream', action='store_true')
    parser.add_argument('--speed', type=float, default=1.0)
    parser.add_argument('--no-text-frontend', action='store_true', help='Disable text normalization frontend')
    parser.add_argument('--backbone', type=str, default='blanken', help='LLM backbone (always uses blanken for cosyvoice2-eu)')
    args = parser.parse_args()

    model_dir = args.model_dir
    if not args.no_hf:
        snapshot_download(repo_id=args.repo_id, local_dir=model_dir)

    cosyvoice = CosyVoice2(
        model_dir,
        load_jit=False,
        load_trt=False,
        load_vllm=False,
        fp16=False,
        setting=args.setting,
        llm_run_id=args.llm_run_id,
        flow_run_id=args.flow_run_id,
        hifigan_run_id=args.hifigan_run_id,
        final=(args.final or not args.no_hf),
        backbone=args.backbone,
    )

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    prompt_speech_16k = load_wav(args.prompt, 16000)
    for i, j in enumerate(
        cosyvoice.inference_cross_lingual(
            args.text,
            prompt_speech_16k,
            stream=args.stream,
            speed=args.speed,
            text_frontend=not args.no_text_frontend,
        )
    ):
        torchaudio.save(args.out if i == 0 else args.out.replace('.wav', f'-{i}.wav'), j['tts_speech'], cosyvoice.sample_rate)


