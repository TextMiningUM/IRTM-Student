# Tier 2 Training — Local RTX 4070, 8 GB VRAM

All scripts assume:
- venv: `c:\Users\jcsch\Documents\Python\UM-Courses\IRTM\.venv310`
- CWD: repository root (`c:\Users\jcsch\Documents\Python\UM-Courses\IRTM`)
- Data: `IRTM-Admin/source/13 agentic_training_data/training_data/cyber_*.json`
- Output: `IRTM-Admin/source/13 agentic_training_data/_models/<name>/`

Run order (each script is independent except DPO, which needs the SFT adapter):

```powershell
& .\.venv310\Scripts\Activate.ps1
$env:PYTHONIOENCODING='utf-8'

# 1. Embedder (~5–10 min)
python -X utf8 IRTM-Admin/source/13 agentic_training_data/_training/train_embedder.py

# 2. Reranker (~5–10 min)
python -X utf8 IRTM-Admin/source/13 agentic_training_data/_training/train_reranker.py

# 3. LoRA-SFT on Qwen2.5-1.5B-Instruct (~30–60 min)
python -X utf8 IRTM-Admin-2025-2026/source/agentic_training_data/_training/train_sft.py

# 4. DPO on top of SFT adapter (~30–60 min)
python -X utf8 IRTM-Admin-2025-2026/source/agentic_training_data/_training/train_dpo.py
```

Each script prints `SAVED: <path>` on success. After all four finish, run the
new §9.7a–§9.7d cells in the notebook to compare Tier 2 against §9.0a–§9.7.

## Outputs
| Script | Saves | Used by |
|---|---|---|
| train_embedder.py | `_models/embedder_v1/` (full SBERT model) | §9.7a (RAG-T2) |
| train_reranker.py | `_models/reranker_v1/` (full CE model) | §9.7a (RAG-T2 rerank) |
| train_sft.py | `_models/sft_qwen15b_lora/` (PEFT adapter) | §9.7b (SFT-T2) |
| train_dpo.py | `_models/dpo_qwen15b_lora/` (PEFT adapter on SFT base) | §9.7c (RLHF-T2), §9.7d (Agent-T2) |

## VRAM notes
- Embedder + reranker are tiny (≤500 MB).
- LoRA-SFT loads Qwen2.5-1.5B in 4-bit (~1.2 GB), trainable LoRA layers add ~30 MB. Peak ≈ 5 GB VRAM with batch_size=2 + grad_accum=4.
- DPO loads SFT-quantized base + LoRA adapter; uses PEFT's "reference-free" path (no separate ref model) so VRAM stays ≈ 5 GB.

## If transformers 5.x breaks something
Pin known-working versions:
```powershell
pip install "transformers==4.44.2" "peft==0.13.0" "trl==0.11.4"
```
