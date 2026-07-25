# IRTM — Student Repository

**Information Retrieval & Text Mining** — Maastricht University  
Department of Advanced Computer Sciences, Faculty of Science and Engineering

## Structure

```
Tutorials/          ← Reference tutorials (read-only, for self-study)
Assignments/        ← Graded assignments (read-only originals)
  tokenization/
  document_representation/
  search_engines/
  measuring_quality/
  structured_representations_1/
  structured_representations_2/
  detecting_patterns_1/
  detecting_patterns_2/
  conversational_search_basics/
  conversational_search_facts/
  agents/
Workspace/          ← Your working directory (copy notebooks here to work on them)
  tokenization/
  document_representation/
  search_engines/
  measuring_quality/
  structured_representations_1/
  structured_representations_2/
  detecting_patterns_1/
  detecting_patterns_2/
  conversational_search_basics/
  conversational_search_facts/
  agents/
SubmittedWork/      ← Copy your finished notebooks here to submit
  tokenization/
  document_representation/
  search_engines/
  measuring_quality/
  structured_representations_1/
  structured_representations_2/
  detecting_patterns_1/
  detecting_patterns_2/
  conversational_search_basics/
  conversational_search_facts/
  agents/
```

## Getting Started

### On JupyterHub (`irtm-course-um.nl`)

1. Open a terminal in JupyterLab
2. Clone this repository:
   ```bash
   git clone https://github.com/TextMiningUM/IRTM-2025-2026.git
   ```
3. Copy the assignment notebook to your `Workspace/` folder (see workflow below)
4. Work on the notebook in `Workspace/`
5. When finished, copy it to `SubmittedWork/` to submit

### Fetching New Assignments

When new assignments are released, pull the latest changes:
```bash
cd IRTM-2025-2026
git pull
```

## Tutorials

The `Tutorials/` folder contains reference notebooks covering all course topics.
These are for self-study and are not graded.

## Assignments

Assignment notebooks are in `Assignments/<topic>/`. Each notebook contains:
- Instructional content explaining the concepts
- **Exercise cells** where you write your code (marked with `# YOUR CODE HERE`)
- **Test cells** that validate your solution (do not modify these)

## Workflow

1. **Copy** the assignment notebook from `Assignments/` to the matching
   `Workspace/` folder. For example:
   ```bash
   cp Assignments/tokenization/01_IRTM_Tokenization_2025_2026.ipynb \
      Workspace/tokenization/
   ```
2. **Work** on the notebook inside `Workspace/<topic>/`. This keeps the
   original in `Assignments/` untouched, so you can always refer back to it
   or get a fresh copy if needed.
3. **Submit** by copying your finished notebook to `SubmittedWork/`:
   ```bash
   cp Workspace/tokenization/01_IRTM_Tokenization_2025_2026.ipynb \
      SubmittedWork/tokenization/
   ```

> **Tip:** The `Workspace/` folder is yours — `git pull` will never overwrite
> files there. This means your in-progress work is safe when you fetch new
> assignments.

## Submission

When you have finished an assignment, copy your completed notebook from
`Workspace/` to the matching folder inside `SubmittedWork/`.

**Important:**
- Keep the original filename — do not rename the notebook.
- Make sure the notebook runs from top to bottom without errors before submitting.
- You can overwrite a previous submission by copying again (latest version counts).
- Deadline: see Canvas for due dates per assignment.
