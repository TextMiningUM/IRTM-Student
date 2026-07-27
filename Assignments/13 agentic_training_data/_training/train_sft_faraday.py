"""
Tier 2 — LoRA-SFT on Qwen2.5-1.5B-Instruct over Faraday SFT trajectories
(faraday_sft_trajectories.json — 108 procedural physics scenarios).

Same QLoRA recipe as train_sft.py, but with a physics-instructor system prompt.
Output:
  _models/sft_qwen15b_lora_faraday/

Note: 108 trajectories is small for full domain SFT. Two epochs typically still
shows a measurable gain on KG/procedural physics questions; expect noisier
metrics than the cyber model trained on 815 trajectories.
"""
from __future__ import annotations
import json
from pathlib import Path
import torch

ROOT     = Path(__file__).resolve().parents[1]
DATA     = ROOT / "training_data"
OUT_DIR  = ROOT / "_models" / "sft_qwen15b_lora_faraday"
BASE     = "Qwen/Qwen2.5-1.5B-Instruct"
SEED     = 13
MAX_LEN  = 1536


def load(name): return json.load(open(DATA / f"{name}.json", encoding="utf-8"))


def render_assistant(steps: list[dict]) -> str:
    out = []
    for i, s in enumerate(steps or [], 1):
        obs = (s.get("observation") or "").strip()
        thg = (s.get("thought") or "").strip()
        act = (s.get("action") or s.get("step_action") or "").strip()
        block = f"Step {i}."
        if obs: block += f"\n  Observation: {obs}"
        if thg: block += f"\n  Thought:     {thg}"
        if act: block += f"\n  Action:      {act}"
        out.append(block)
    return "\n".join(out) if out else "(no steps recorded)"


def build_dataset(tokenizer):
    from datasets import Dataset
    trajs = load("faraday_sft_trajectories")
    rows = []
    for t in trajs:
        scenario = (t.get("scenario") or "").strip()
        chapter  = (t.get("chapter") or "").strip()
        steps    = t.get("steps") or []
        if not scenario or not steps:
            continue
        user_msg = f"Walk me through this physics procedure: {scenario}"
        if chapter:
            user_msg += f"\nChapter: {chapter}"
        asst_msg = render_assistant(steps)
        chat = [
            {"role": "system",    "content": "You are a careful physics instructor in the tradition of Faraday's Experimental Researches. Answer with structured procedural steps."},
            {"role": "user",      "content": user_msg},
            {"role": "assistant", "content": asst_msg},
        ]
        text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=False)
        rows.append({"text": text})
    print(f"Faraday SFT examples: {len(rows)}")
    return Dataset.from_list(rows)


def main() -> None:
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer, SFTConfig

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
    model = AutoModelForCausalLM.from_pretrained(
        BASE,
        quantization_config=bnb,
        device_map={"": 0},
        trust_remote_code=True,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    ds = build_dataset(tok)

    cfg = SFTConfig(
        output_dir=str(OUT_DIR),
        num_train_epochs=2,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        gradient_checkpointing=True,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=10,
        save_strategy="epoch",
        save_total_limit=1,
        bf16=True,
        optim="paged_adamw_8bit",
        max_length=MAX_LEN,
        packing=False,
        dataset_text_field="text",
        report_to="none",
        seed=SEED,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=ds,
        args=cfg,
        processing_class=tok,
    )
    # Auto-resume if a previous run left a *complete* checkpoint behind.
    # Skip checkpoints missing trainer_state.json (partial/crashed saves).
    ckpts = sorted(OUT_DIR.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[-1]))
    ckpts = [c for c in ckpts if (c / "trainer_state.json").is_file()]
    resume = str(ckpts[-1]) if ckpts else None
    if resume:
        print(f"resuming Faraday SFT from {resume}")
    trainer.train(resume_from_checkpoint=resume)
    trainer.save_model(str(OUT_DIR))
    tok.save_pretrained(str(OUT_DIR))
    print(f"SAVED: {OUT_DIR}")


if __name__ == "__main__":
    main()
