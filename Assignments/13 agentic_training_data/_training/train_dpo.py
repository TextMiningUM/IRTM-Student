"""
Tier 2 — DPO on the SFT adapter, over 1492 cyber RLHF preference pairs.

Each preference example becomes:
    prompt   = "Context: <context>\nWhat is the recommended secure action and why?"
    chosen   = "<chosen_action>\nReasoning: <chosen_reasoning>"
    rejected = "<rejected_action>\nReasoning: <rejected_reasoning>"

We start from `_models/sft_qwen15b_lora` (LoRA adapter) and continue training
in DPO mode with the same base model in 4-bit. PEFT's reference-free path keeps
VRAM ≈ 5 GB.

Output:
  IRTM-Admin/source/13 agentic_training_data/_models/dpo_qwen15b_lora/
"""
from __future__ import annotations
import json
from pathlib import Path
import torch

ROOT       = Path(__file__).resolve().parents[1]
DATA       = ROOT / "training_data"
SFT_DIR    = ROOT / "_models" / "sft_qwen15b_lora"
OUT_DIR    = ROOT / "_models" / "dpo_qwen15b_lora"
BASE       = "Qwen/Qwen2.5-1.5B-Instruct"
SEED       = 13
MAX_LEN    = 1024
MAX_PROMPT = 512


def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def build_dataset():
    from datasets import Dataset
    pairs = load("cyber_rlhf_pairs")
    rows = []
    for p in pairs:
        ctx  = (p.get("context") or "").strip()
        ca   = (p.get("chosen_action") or "").strip()
        cr   = (p.get("chosen_reasoning") or "").strip()
        ra   = (p.get("rejected_action") or "").strip()
        rr   = (p.get("rejected_reasoning") or "").strip()
        if not (ca and ra):
            continue
        prompt = f"Context: {ctx}\nWhat is the recommended secure action and why?"
        chosen = f"{ca}\nReasoning: {cr}".strip()
        rejected = f"{ra}\nReasoning: {rr}".strip()
        rows.append({"prompt": prompt, "chosen": chosen, "rejected": rejected})
    print(f"DPO pairs: {len(rows)}")
    return Dataset.from_list(rows)


def main() -> None:
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel, LoraConfig
    from trl import DPOTrainer, DPOConfig

    # Resolve the SFT adapter directory: prefer the finalised root, else the latest checkpoint.
    adapter_dir = SFT_DIR
    if not (SFT_DIR / "adapter_config.json").exists():
        ckpts = sorted(SFT_DIR.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[-1]))
        if not ckpts:
            raise SystemExit(f"missing SFT adapter at {SFT_DIR}; run train_sft.py first.")
        adapter_dir = ckpts[-1]
        print(f"note: root adapter not found; falling back to {adapter_dir}")

    torch.manual_seed(SEED)
    OUT_DIR.parent.mkdir(parents=True, exist_ok=True)

    print(f"loading tokenizer/base: {BASE}")
    tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map={"": 0},
        trust_remote_code=True,
    )
    base.config.use_cache = False

    # Load the SFT adapter and continue training (merge=False, trainable=True).
    print(f"attaching SFT adapter: {adapter_dir}")
    model = PeftModel.from_pretrained(base, str(adapter_dir), is_trainable=True)

    ds = build_dataset()

    cfg = DPOConfig(
        output_dir=str(OUT_DIR),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        learning_rate=5e-6,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=1,
        bf16=True,
        optim="paged_adamw_8bit",
        max_length=MAX_LEN,
        beta=0.1,
        report_to="none",
        seed=SEED,
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=None,            # PEFT reference-free path
        args=cfg,
        train_dataset=ds,
        processing_class=tok,
    )
    trainer.train()
    trainer.save_model(str(OUT_DIR))
    tok.save_pretrained(str(OUT_DIR))
    print(f"SAVED: {OUT_DIR}")


if __name__ == "__main__":
    main()
