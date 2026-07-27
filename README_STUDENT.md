# IRTM — Student Repository

**Information Retrieval & Text Mining** — Maastricht University  
Department of Advanced Computer Sciences, Faculty of Science and Engineering  
**Academic Year: 2026-2027**

## Structure

```
Tutorials/                   ← Reference tutorials (read-only, for self-study)
Assignments/                 ← Graded assignments (released by instructors)
  01 tokenization 2/
  02 document_representation/
  03 measuring_quality/
  04 dense_retrieval/
  05 search_engines/
  06 structured_representations_1/
  07 structured_representations_2/
  08 detecting_patterns_1/
  09 detecting_patterns_2/
  10 conversational_search_basics/
  11 conversational_search_facts/
  12 agents/
  13 agentic_training_data/
Personal Workspace/          ← Your working directory (copy notebooks here to work)
Submitted Work/              ← Copy your finished notebooks here to submit
Course Materials/            ← Lecture slides and additional resources
```

## Getting Started

### On JupyterHub (`irtm-course-um.nl`)

1. Open a terminal in JupyterLab
2. Clone this repository:
   ```bash
   git clone https://github.com/TextMiningUM/IRTM-Student.git
   ```
3. Copy the assignment notebook to your `Personal Workspace/` folder (see workflow below)
4. Work on the notebook in `Personal Workspace/`
5. When finished, copy it to `Submitted Work/` to submit

### Fetching New Assignments

When new assignments are released, pull the latest changes:
```bash
cd IRTM-Student
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

1. **Copy** the assignment notebook from `Assignments/` to your
   `Personal Workspace/` folder. For example:
   ```bash
   cp "Assignments/01 tokenization 2/01_IRTM_Tokenization_2026_2027.ipynb" \
      "Personal Workspace/"
   ```
2. **Work** on the notebook inside `Personal Workspace/`. This keeps the
   original in `Assignments/` untouched, so you can always refer back to it
   or get a fresh copy if needed.
3. **Submit** by copying your finished notebook to `Submitted Work/`:
   ```bash
   cp "Personal Workspace/01_IRTM_Tokenization_2026_2027.ipynb" \
      "Submitted Work/"
   ```

> **Tip:** The `Personal Workspace/` folder is yours — `git pull` will never overwrite
> files there. This means your in-progress work is safe when you fetch new
> assignments.

## Submission

When you have finished an assignment, copy your completed notebook from
`Personal Workspace/` to `Submitted Work/`.

**Important:**
- Keep the original filename — do not rename the notebook.
- Make sure the notebook runs from top to bottom without errors before submitting.
- You can overwrite a previous submission by copying again (latest version counts).
- Deadline: see Canvas for due dates per assignment.
