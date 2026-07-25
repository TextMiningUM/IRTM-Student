# IRTM Tutorial Codebase Guide for AI Agents

## Project Overview
This repository contains Jupyter Notebook tutorials for the **Information Retrieval & Text Mining (IRTM)** course at Maastricht University's Faculty of Science and Engineering (Department of Advanced Computer Sciences). The tutorials are designed for Google Colab execution and cover core NLP/IR concepts.

### Key Characteristics
- **Format**: Jupyter Notebooks (.ipynb) in Python
- **Target Runtime**: Google Colab (not local execution)
- **Course Years**: Contains versions for 2024-2025, 2025-2026, and 2026-2027
- **Audience**: University students learning IR and Text Mining fundamentals

## Architecture & Tutorial Structure

### Primary Tutorial Index
- [IRTM_Tutorial_index_2024_2025.ipynb](Tutorials/IRTM_Tutorial_index_2024_2025.ipynb) - Master index linking all tutorials
- [IRTM_Tutorial_intro_2024_2025.ipynb](Tutorials/IRTM_Tutorial_intro_2024_2025.ipynb) - Colab setup, environment, shell, magics, Google Drive integration
- [IRTM_Tutorial_query_2024_2025.ipynb](Tutorials/IRTM_Tutorial_query_2024_2025.ipynb) - Query processing and evaluation tools (trec_eval)

### Core Concept Tutorials
1. **Tokenization** ([01_IRTM_Tokenization_2025_2026.ipynb](Tutorials/01_IRTM_Tokenization_2025_2026.ipynb))
   - Text extraction from HTML/PDF, encoding normalization (UTF-8)
   - NLTK library usage for tokenization
   - Stanford NLP tools integration
   - Language-specific processing (Western European languages)

2. **Document Indexing** ([IRTM_Tutorial_index_2024_2025.ipynb](Tutorials/IRTM_Tutorial_index_2024_2025.ipynb))
   - Apache Lucene indexing via Anserini toolkit
   - MS MARCO passage collection indexing
   - Maven build system for Java-based tools

3. **Text Classification (Unsupervised)** ([13_IRTM_Text_Classification_Unsupervised.ipynb](Tutorials/13_IRTM_Text_Classification_Unsupervised.ipynb))
   - Clustering and classification without labeled data

4. **Advanced Topics**
   - [Topic Modeling](Tutorials/IRTM_Topic_Modeling_Tutorial_2024_2025.ipynb) - LDA and unsupervised topic discovery
   - [Retrieval Augmented Generation (RAG)](Tutorials/IRTM_Retrieval_Augmented_Generation_(RAG)_2024_2025.ipynb) - Modern retrieval patterns
   - [Neural Reranking](Tutorials/IRTM_Neural_Reranking_2024_2024%20runned%20version.ipynb) - Deep learning ranking models
   - Information Extraction, Preprocessing, Document Representation, Quality Measurement

## Development Patterns & Conventions

### Notebook Cell Organization
- **Markdown cells**: Educational content explaining concepts, include external links to resources
- **Code cells**: Executable Python/Shell commands, usually preceded by setup/context markdown
- **Cell structure**: Each tutorial introduces concepts progressively, building on prerequisites
- **Exercise cells**: Include interactive tasks (marked as "Exercise #N") for students to complete

### Colab-Specific Patterns
```python
# System commands prefixed with !
!apt-get install -y openjdk-11-jdk-headless

# Cell magics for verbose operations
%%capture
!pip install package_name

# Environment variables
%env JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Google Drive mounting (common in tutorials)
from google.colab import drive
drive.mount('/content/drive')
```

### External Tool Integration
- **Apache Anserini**: Clone from GitHub, build with Maven for indexing
- **NLTK**: Used for tokenization and corpus access; requires `nltk.download()` calls
- **BeautifulSoup**: HTML/XML parsing for web content extraction
- **trec_eval**: NIST evaluation tool for search result ranking assessment
- **Java 11 + Maven**: Required for Anserini indexing pipeline

### Data & Storage Conventions
- Tutorials assume Google Drive as persistent storage
- Files are typically small datasets (MS MARCO passages, movie reviews corpus)
- Local execution uses `/content` directory in Colab; maps to Google Drive via mounting
- Character encoding: UTF-8 normalized from various formats

## Key Dependencies & Tools

| Tool | Purpose | Integration |
|------|---------|-------------|
| NLTK | Tokenization, corpus access | Direct Python import |
| BeautifulSoup | HTML/XML parsing | Direct Python import |
| Apache Anserini | Index creation (Java) | Git clone + Maven build |
| Apache Lucene | Underlying search library | Via Anserini |
| trec_eval | IR evaluation metrics | Compiled binary from source |
| scikit-learn | ML algorithms (clustering) | Direct Python import |
| spaCy / Stanford NLP | Advanced NLP | Optional, mentioned in tutorials |

## Common Development Tasks

### Adding New Tutorial Content
1. Create `.ipynb` file following naming convention: `NN_IRTM_[Topic]_2025_2026.ipynb`
2. Start with Maastricht University logo markdown cell and course header
3. Include "Start by copying this into your Google Drive!!" at top
4. Structure: Introduction → Theory → Code Examples → Exercises
5. Reference [01_IRTM_Tokenization_2025_2026.ipynb](Tutorials/01_IRTM_Tokenization_2025_2026.ipynb) as template

### Updating Existing Tutorials
- Maintain backward compatibility (keep 2024-2025 versions as reference)
- Test all external tool calls (shell commands) in actual Colab environment
- Verify Java/Maven setup cells work before publishing
- Update [IRTM_Tutorial_index_2024_2025.ipynb](Tutorials/IRTM_Tutorial_index_2024_2025.ipynb) with new content links

### Debugging Patterns
- **Import issues**: Use `!pip list` to verify package versions in Colab
- **Shell command failures**: Remember to prefix with `!` in notebooks
- **Java/Maven errors**: Check `%env JAVA_HOME` is set correctly
- **NLTK data missing**: Ensure `nltk.download()` calls run before corpus usage

## Important File References
- [.gitignore](.gitignore) - Ignores `.DS_Store`, VS project files (`.vs/`), `.suo` user files
- Git repo initialized; preserve commit history for tutorial evolution tracking

## Critical Know-Before-You-Code Points

1. **Colab Environment**: Tutorials run in ephemeral Colab kernels, not persistent local environments
2. **Tool Installation**: Java 11, Maven, and trec_eval require explicit installation cells (see indexing tutorials)
3. **Language Scope**: Tokenization and preprocessing focused on Western European languages (English, German, Dutch, etc.)
4. **Evaluation Metrics**: trec_eval is the de-facto standard for IR system evaluation in this course
5. **Versioning**: Maintain 2024-2025 versions for reference; new features in 2025-2026 versions
6. **Google Drive Integration**: Essential for persistent storage; mounting pattern established in intro tutorial

## References for Contributors
- Anserini Repository: https://github.com/castorini/anserini
- NLTK Documentation: https://www.nltk.org/
- NIST trec_eval: https://github.com/usnistgov/trec_eval
- Google Colab Guide: https://colab.research.google.com/notebooks/
- MS MARCO Dataset: http://www.msmarco.org/
