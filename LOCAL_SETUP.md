# Running IRTM Notebooks on Your Own Machine

> **Recommended:** Use the course JupyterHub at
> <https://www.irtm-course-um.nl> — everything is pre-installed and ready
> to go. The instructions below are **only** for students who prefer to
> work locally (e.g. for faster GPU access, offline work, or when the
> cluster is busy).

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Create a Python Environment](#3-create-a-python-environment)
4. [Install Python Dependencies](#4-install-python-dependencies)
5. [Install Java (for Tutorial 03)](#5-install-java-for-tutorial-03)
6. [Download NLTK Data](#6-download-nltk-data)
7. [Download spaCy Models](#7-download-spacy-models)
8. [GPU Support (optional but recommended)](#8-gpu-support-optional-but-recommended)
9. [OpenAI API Key (Tutorials 11 & 12)](#9-openai-api-key-tutorials-11--12)
10. [Tutorial-specific Notes](#10-tutorial-specific-notes)
11. [Submitting Your Work](#11-submitting-your-work)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.10 (recommended — same as the cluster). Versions 3.9–3.11 should work. Python 3.12+ may cause compatibility issues with some packages. |
| **pip** | Latest version (`python -m pip install --upgrade pip`) |
| **Git** | To clone the repository |
| **Java JDK 11+** | Only needed for Tutorial 03 (Search Engines / Pyserini) |
| **OS** | Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+) |
| **RAM** | Minimum 8 GB; 16 GB recommended |
| **Disk space** | ~10 GB free (for packages, models, and datasets) |

---

## 2. Clone the Repository

```bash
git clone https://github.com/TextMiningUM/IRTM-2025-2026.git
cd IRTM-2025-2026
```

---

## 3. Create a Python Environment

We strongly recommend using a **virtual environment** to avoid conflicts with
other projects.

### Option A — conda (recommended if you have Anaconda/Miniconda)

```bash
conda create -n irtm python=3.10 -y
conda activate irtm
```

### Option B — venv (built-in)

```bash
python -m venv .venv

# Activate on Linux/macOS:
source .venv/bin/activate

# Activate on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Activate on Windows (cmd):
.\.venv\Scripts\activate.bat
```

---

## 4. Install Python Dependencies

A `requirements.txt` is provided in the repository root:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs **all** packages needed across all 11 tutorials. The full
install takes roughly 5–15 minutes depending on your network and hardware.

> **Note on PyTorch:** The command above installs the CPU version of PyTorch.
> If you have an NVIDIA GPU, see [Section 8](#8-gpu-support-optional-but-recommended)
> for GPU-accelerated installation.

---

## 5. Install Java (for Tutorial 03)

Tutorial 03 (*Search Engines*) uses **Pyserini**, which depends on Apache
Lucene and requires **Java JDK 11 or higher**.

### Windows

1. Download the JDK from <https://adoptium.net/> (Temurin 17 LTS recommended).
2. Run the installer.
3. Set the `JAVA_HOME` environment variable:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-17...", "User")
   ```
4. Restart your terminal and verify:
   ```bash
   java -version
   ```

### macOS

```bash
brew install openjdk@17
sudo ln -sfn $(brew --prefix openjdk@17)/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

> **Tip:** Add the `JAVA_HOME` export to your `~/.bashrc` / `~/.zshrc` so it
> persists across sessions.

If you don't need Tutorial 03, you can skip Java entirely.

---

## 6. Download NLTK Data

Several tutorials rely on NLTK corpora and models. Run this **once** after
installing the Python packages:

```python
import nltk
nltk.download([
    'punkt',
    'punkt_tab',
    'stopwords',
    'wordnet',
    'omw-1.4',
    'words',
    'movie_reviews',
    'brown',
    'universal_tagset',
    'book',
    'tagsets_json',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng',
    'treebank',
    'vader_lexicon',
    'maxent_ne_chunker',
    'maxent_ne_chunker_tab',
])
```

Or from the command line:

```bash
python -m nltk.downloader punkt punkt_tab stopwords wordnet omw-1.4 words movie_reviews brown universal_tagset book tagsets_json averaged_perceptron_tagger averaged_perceptron_tagger_eng treebank vader_lexicon maxent_ne_chunker maxent_ne_chunker_tab
```

---

## 7. Download spaCy Models

Tutorial 10 (*Conversational Search Basics*) requires a spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

---

## 8. GPU Support (optional but recommended)

A CUDA-capable **NVIDIA GPU** significantly speeds up the deep-learning
tutorials (04, 06, 07, 08, 09). All tutorials include CPU fallbacks, so a GPU
is **not** strictly required — they will just run slower.

### Which tutorials benefit from a GPU?

| Tutorial | Task | GPU benefit |
|---|---|---|
| 04 — Measuring Quality | GPT-2 perplexity, BERTScore | Moderate |
| 06 — Structured Representations 1 | Coreference resolution (F-Coref) | Moderate |
| 07 — Structured Representations 2 | BERT NER fine-tuning | **High** (~2–3 min on RTX 4070 vs ~15+ min on CPU) |
| 08 — Detecting Patterns 1 | BERT sentiment fine-tuning on IMDB | **High** (~2–4 min on RTX 4070 vs ~20+ min on CPU) |
| 09 — Detecting Patterns 2 | BERT masked LM, BERTopic | Moderate |

### GPU Compatibility

**Works with ALL modern NVIDIA GPUs:**
- ✅ RTX 30xx series (3060, 3070, 3080, 3090)
- ✅ RTX 40xx series (4060, 4070, 4080, 4090)
- ✅ RTX 50xx series (5080, 5090) — when available
- ✅ Professional cards (A100, H100, L40, RTX 6000, etc.)
- ✅ Older cards: GTX 1660, RTX 20xx series

**Minimum requirement:** NVIDIA GPU with Compute Capability 5.0+ (GTX 900 series from 2014+)

### VRAM Requirements

The amount of GPU memory determines which models and batch sizes you can use:

| GPU VRAM | Suitable for | Typical models | Batch size |
|---|---|---|---|
| 4–6 GB | Basic training | DistilBERT, small models | 4–8 |
| 8–12 GB | All tutorials | BERT-base, GPT-2 | 8–16 |
| 16–24 GB | Large batches | BERT-large, larger datasets | 16–32 |
| 24+ GB | Research experiments | Multiple models, ensembles | 32+ |

> **Note:** All IRTM tutorials work fine with 8GB VRAM. If you have less,
> reduce batch sizes as needed (see Troubleshooting below).

### Installing PyTorch with CUDA

First, **uninstall** any existing PyTorch:

```bash
pip uninstall torch torchvision torchaudio -y
```

Install PyTorch with CUDA 12.4 (works on all NVIDIA drivers 525.60.13+):

```bash
# Windows / Linux / macOS
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

> **Why cu124?** CUDA 12.4 is **backward compatible** with all modern GPUs.
> It works whether your `nvidia-smi` shows CUDA 11.x, 12.x, or 13.x.
> The driver version matters more than the CUDA version shown.

### Verify GPU Access

Create a test script `test_gpu.py`:

```python
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Check VRAM
    props = torch.cuda.get_device_properties(0)
    print(f"VRAM: {props.total_memory / 1024**3:.1f} GB")
    print(f"Compute capability: {props.major}.{props.minor}")
else:
    print("No GPU detected — using CPU only")
```

Run it:

```bash
python test_gpu.py
```

Expected output:
```
PyTorch version: 2.6.0+cu124
CUDA available: True
CUDA version: 12.4
GPU: NVIDIA GeForce RTX 3090
VRAM: 24.0 GB
Compute capability: 8.6
```

### Troubleshooting

**Problem:** `CUDA available: False`

**Solutions:**
1. Check if you have an NVIDIA GPU: `nvidia-smi`
2. Update NVIDIA drivers: <https://www.nvidia.com/Download/index.aspx>
3. Reinstall PyTorch with CUDA (see above)
4. Verify you're using the correct Python environment

**Problem:** `OutOfMemoryError` during training

**Solutions:**
1. **Reduce batch size** in the notebook (e.g., `batch_size=4` instead of `batch_size=16`)
2. **Enable mixed precision training:**
   ```python
   trainer = Trainer(..., fp16=True)  # or bf16=True for newer GPUs
   ```
3. **Clear GPU cache:**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```
4. **Use gradient accumulation** to simulate larger batches:
   ```python
   trainer = Trainer(..., per_device_train_batch_size=4, gradient_accumulation_steps=4)
   # Effective batch size = 4 × 4 = 16
   ```

**Problem:** Training is slow even with GPU

**Check:**
1. Verify GPU is actually being used:
   ```python
   print(next(model.parameters()).device)  # Should show 'cuda:0'
   ```
2. Monitor GPU utilization: `nvidia-smi -l 1` (refreshes every second)
3. Ensure data is on GPU: `inputs = inputs.to('cuda')`

---

## 9. OpenAI API Key (Tutorials 11 & 12)

Tutorials 11 (*Conversational Search — Sticking to the Facts*) and 12
(*Agents*) use the **OpenAI API** with the `gpt-4o-mini` model. You will need:

1. An OpenAI account with **billing enabled** at <https://platform.openai.com>.
2. An API key generated at <https://platform.openai.com/api-keys>.

The cost is modest — expect roughly **€1–€3** for completing both tutorials
with `gpt-4o-mini`.

The notebooks will prompt you for the key using `getpass` (it is never stored
in the notebook). Alternatively, set it as an environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
```

> **Important:** Never commit your API key to Git. The `.gitignore` should
> already exclude sensitive files, but double-check before pushing.

---

## 10. Tutorial-specific Notes

### Tutorial 01 — Tokenization
- Fetches a live webpage via `urllib.request`; requires internet access.

### Tutorial 03 — Search Engines
- Requires **Java JDK 11+** (see [Section 5](#5-install-java-for-tutorial-03)).
- On first run, Pyserini downloads the **MS MARCO passage index** (~2 GB).
  This is cached for subsequent runs.
- Downloads a text file from Project Gutenberg (Sherlock Holmes).

### Tutorials 07 & 11 — Structured Representations 2 / Facts
- Tutorial 07 generates several output files (`chunks.json`,
  `sherlock_kg.json`, `qa_test_set.json`, `atomic_facts.json`, and `.txt`
  chunk files) that are **required inputs** for Tutorial 11.
- **Run Tutorial 07 before Tutorial 11.**

### Tutorial 06 — Structured Representations 1
- Uses a pre-trained CRF model file (`model.crf.tagger`) that is provided in
  the `Tutorials/` folder. Make sure this file is present.

### Tutorial 12 — Agents
- Uses the OpenAI Agents SDK (`openai-agents`). Requires `openai>=1.40.0`.

---

## 11. Submitting Your Work

Even if you develop locally, you must **submit via the JupyterHub**:

1. Before submitting, **restart the kernel and run all cells** to ensure
   the notebook executes cleanly from top to bottom.
2. Upload your completed notebook to the JupyterHub by copying it into the
   appropriate `SubmittedWork/<topic>/` folder on the cluster.
3. Keep the **original filename** — do not rename the notebook.

> **Tip:** As a final check, download your notebook from JupyterHub after
> uploading and verify it opens correctly.

---

## 12. Troubleshooting

### "ModuleNotFoundError: No module named '...'"
You likely missed a dependency. Make sure you installed from the provided
`requirements.txt` and that your virtual environment is activated.

### Pyserini / Java errors
Ensure `JAVA_HOME` is set and points to a valid JDK 11+ installation.
Test with `java -version` in your terminal.

### CUDA / GPU not detected
- Verify you installed the CUDA version of PyTorch (not the CPU version).
- Check that your NVIDIA drivers are up-to-date: `nvidia-smi`.
- Ensure `torch.cuda.is_available()` returns `True`.

### NLTK data not found
Re-run the NLTK download commands in [Section 6](#6-download-nltk-data).
You can also manually set the NLTK data path:
```python
import nltk
nltk.data.path.append('/path/to/your/nltk_data')
```

### HuggingFace model download is slow
Models are cached in `~/.cache/huggingface/`. The first load takes time;
subsequent loads are instant. If your network is restricted, consider
downloading models on a different network and copying the cache folder.

### Package version conflicts
If you encounter version incompatibilities, try creating a fresh environment:
```bash
conda create -n irtm-fresh python=3.10 -y
conda activate irtm-fresh
pip install -r requirements.txt
```

### "RuntimeError: CUDA out of memory"
Reduce the batch size in training cells, or switch to CPU by setting:
```python
device = torch.device("cpu")
```

---

## Summary of External Services & Costs

| Service | Tutorials | Cost | Required? |
|---|---|---|---|
| Course JupyterHub | All | Free | Primary platform |
| OpenAI API | 11, 12 | ~€1–€3 | Yes, for these tutorials |
| Internet access | 01, 03, 04, 07, 08 | — | Yes (data downloads) |

---

*Last updated: February 2026*
