"""
IRTM Dataset Loader
Smart loader that downloads datasets from Google Cloud Storage with fallback.

Usage in notebooks:
    from dataset_loader import load_irtm_dataset
    
    # Load Sherlock Holmes corpus
    corpus_text = load_irtm_dataset("sherlock_holmes")
    
    # Load CoNLL-2003 NER dataset
    dataset = load_irtm_dataset("conll2003")
    
    # Load agentic training data
    training_data = load_irtm_dataset("agentic_training_data")
    
    # Load MS MARCO index (for BM25 search)
    searcher = load_irtm_dataset("msmarco_v1_passage_index")
    
    # Load TREC-DL 2019 topics and qrels
    topics, qrels = load_irtm_dataset("trec_dl_2019")
"""

import requests
import tarfile
import hashlib
import json
from pathlib import Path
from datasets import load_dataset, load_from_disk
from tqdm import tqdm

# Configuration
CACHE_DIR = Path.home() / ".cache" / "irtm_datasets"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Google Cloud Storage base URL
GCS_BASE_URL = "https://storage.googleapis.com/um-irtm-datasets"

# Dataset registry
DATASETS_REGISTRY = {
    "agentic_training_data": {
        "filename": "agentic_training_data.tar.gz",
        "sha256": "cf4c1b313ca9bfc7d689b49f02441c37d562324ecac7e315568c9f65918fdc70",
        "type": "json_collection",
        "description": "Cybersecurity agentic training data (RAG, SFT, RLHF, etc.)"
    },
    "sherlock_holmes": {
        "filename": "sherlock_holmes.tar.gz",
        "sha256": "4bccff1febe7bfb4d28ce85b8e0656f1a6ff907aee37b658a1b7f157a24c6d83",
        "type": "text",
        "url_fallback": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
        "description": "The Adventures of Sherlock Holmes corpus"
    },
    "conll2003": {
        "filename": "conll2003.tar.gz",
        "sha256": "47b2be26632d10c52d436d02ec6deea9902069d0200c51e2dc4a78b515c03784",
        "type": "huggingface_disk",
        "hf_fallback": {
            "name": "eriktks/conll2003"
        },
        "description": "CoNLL-2003 NER dataset"
    },
    "msmarco_v1_passage_index": {
        "filename": "msmarco_v1_passage_index.tar.gz",
        "sha256": "1d09c0d54f1ff66764834146644528c689df072ff7e0d50102010c7a3093183b",
        "type": "pyserini_index",
        "pyserini_fallback": "msmarco-v1-passage",
        "description": "MS MARCO v1 passage corpus Lucene index (8.8M docs)"
    },
    "trec_dl_2019": {
        "filename": "trec_dl_2019.tar.gz",
        "sha256": "aaf5a7781561123cdc395d67f6279923f3ad3a3b8857ebd48394309fe6fe6ffc",
        "type": "pyserini_topics",
        "pyserini_fallback": {
            "topics": "dl19-passage",
            "qrels": "dl19-passage"
        },
        "description": "TREC Deep Learning 2019 topics and qrels"
    }
}


def verify_checksum(file_path, expected_sha256):
    """Verify SHA256 checksum of downloaded file."""
    if expected_sha256 is None:
        print("⚠️  No checksum available, skipping verification")
        return True
    
    print("🔐 Verifying checksum...")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    computed = sha256_hash.hexdigest()
    if computed == expected_sha256:
        print("✅ Checksum verified")
        return True
    else:
        print(f"❌ Checksum mismatch!")
        print(f"   Expected: {expected_sha256}")
        print(f"   Got:      {computed}")
        return False


def download_from_gcs(dataset_name, config):
    """Download dataset package from Google Cloud Storage."""
    
    url = f"{GCS_BASE_URL}/{config['filename']}"
    output_path = CACHE_DIR / config['filename']
    
    # Check if already downloaded and verified
    if output_path.exists():
        if verify_checksum(output_path, config['sha256']):
            print("✅ Dataset already cached and verified")
            return output_path
        else:
            print("⚠️  Cached file failed verification, re-downloading...")
            output_path.unlink()
    
    print(f"📥 Downloading from Google Cloud Storage: {config['filename']}")
    print(f"   URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, stream=True, timeout=60, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=config['filename']
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
        
        # Verify checksum
        if not verify_checksum(output_path, config['sha256']):
            output_path.unlink()
            raise ValueError("Checksum verification failed")
        
        return output_path
    
    except Exception as e:
        print(f"❌ Failed to download from GCS: {e}")
        if output_path.exists():
            output_path.unlink()
        return None


def extract_tarball(tar_path, extract_dir):
    """Extract a .tar.gz file."""
    print(f"📦 Extracting {tar_path.name}...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(extract_dir)
    print(f"✅ Extracted to {extract_dir}")


def load_irtm_dataset(dataset_name):
    """
    Load an IRTM dataset.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'sherlock_holmes', 'conll2003', 'agentic_training_data')
    
    Returns:
        Dataset content (format depends on dataset type)
    """
    if dataset_name not in DATASETS_REGISTRY:
        raise ValueError(
            f"Unknown dataset: {dataset_name}\n"
            f"Available: {', '.join(DATASETS_REGISTRY.keys())}"
        )
    
    config = DATASETS_REGISTRY[dataset_name]
    print(f"\n🔍 Loading dataset: {dataset_name}")
    print(f"   {config['description']}")
    
    # Check if already extracted in cache
    extract_dir = CACHE_DIR / dataset_name
    
    if extract_dir.exists():
        print(f"✅ Using cached dataset from {extract_dir}")
    else:
        # Try downloading from GCS
        tar_path = download_from_gcs(dataset_name, config)
        
        if tar_path is None:
            # Fallback to original source
            print("\n⚠️  GCS download failed, trying fallback source...")
            
            if config['type'] == 'huggingface_disk' and 'hf_fallback' in config:
                print(f"📥 Loading from HuggingFace: {config['hf_fallback']['name']}")
                dataset = load_dataset(config['hf_fallback']['name'])
                # Save to cache for next time
                dataset.save_to_disk(str(extract_dir))
                return dataset
            
            elif config['type'] == 'text' and 'url_fallback' in config:
                print(f"📥 Downloading from: {config['url_fallback']}")
                response = requests.get(config['url_fallback'], timeout=60)
                response.raise_for_status()
                text = response.text
                
                # Clean Gutenberg headers
                start_marker = "*** START OF"
                end_marker = "*** END OF"
                start_idx = text.find(start_marker)
                if start_idx != -1:
                    start_idx = text.find('\n', start_idx) + 1
                else:
                    start_idx = 0
                end_idx = text.find(end_marker)
                if end_idx == -1:
                    end_idx = len(text)
                
                cleaned_text = text[start_idx:end_idx].strip()
                
                # Save to cache
                extract_dir.mkdir(parents=True, exist_ok=True)
                text_file = extract_dir / "sherlock_holmes.txt"
                text_file.write_text(cleaned_text, encoding='utf-8')
                
                return cleaned_text
            
            elif config['type'] == 'pyserini_index' and 'pyserini_fallback' in config:
                print(f"📥 Loading from Pyserini prebuilt: {config['pyserini_fallback']}")
                try:
                    from pyserini.search.lucene import LuceneSearcher
                    searcher = LuceneSearcher.from_prebuilt_index(config['pyserini_fallback'])
                    print(f"✅ Loaded from Pyserini: {searcher.num_docs:,} documents")
                    return searcher
                except ImportError:
                    raise ImportError("Pyserini not installed. Install: pip install pyserini")
            
            elif config['type'] == 'pyserini_topics' and 'pyserini_fallback' in config:
                print(f"📥 Loading from Pyserini: topics={config['pyserini_fallback']['topics']}")
                try:
                    from pyserini.search import get_topics, get_qrels
                    topics = get_topics(config['pyserini_fallback']['topics'])
                    qrels = get_qrels(config['pyserini_fallback']['qrels'])
                    print(f"✅ Loaded from Pyserini: {len(topics)} topics, {len(qrels)} qrels")
                    return topics, qrels
                except ImportError:
                    raise ImportError("Pyserini not installed. Install: pip install pyserini")
            
            else:
                raise RuntimeError(f"No fallback available for {dataset_name}")
        
        # Extract the downloaded tar.gz
        extract_tarball(tar_path, CACHE_DIR)
    
    # Load the dataset based on type
    if config['type'] == 'json_collection':
        # Load all JSON files from the directory
        json_files = list(extract_dir.glob("**/*.json"))
        data = {}
        for json_file in json_files:
            if not json_file.name.startswith('.'):  # Skip hidden files
                with open(json_file, 'r', encoding='utf-8') as f:
                    data[json_file.stem] = json.load(f)
        print(f"✅ Loaded {len(data)} JSON files")
        return data
    
    elif config['type'] == 'text':
        # Load text file
        text_file = extract_dir / "sherlock_holmes.txt"
        if not text_file.exists():
            # Try alternative path (direct extract)
            text_file = list(extract_dir.glob("**/*.txt"))[0]
        
        text = text_file.read_text(encoding='utf-8')
        print(f"✅ Loaded text: {len(text):,} characters")
        return text
    
    elif config['type'] == 'huggingface_disk':
        # Load HuggingFace dataset from disk
        dataset = load_from_disk(str(extract_dir))
        print(f"✅ Loaded dataset with splits: {list(dataset.keys())}")
        return dataset
    
    elif config['type'] == 'pyserini_index':
        # Load Pyserini Lucene index
        try:
            from pyserini.search.lucene import LuceneSearcher
            
            # The tarball extracts to a directory without the "_index" suffix
            # e.g., msmarco_v1_passage_index.tar.gz → msmarco_v1_passage/
            actual_extract_dir = extract_dir.parent / extract_dir.name.replace("_index", "")
            
            # Find the index directory by looking for Lucene segment files
            index_path = None
            
            # Check if the main directory contains Lucene segments
            if list(actual_extract_dir.glob("segments*")):
                index_path = actual_extract_dir
            else:
                # Look for subdirectories with Lucene segments
                for p in actual_extract_dir.rglob("*"):
                    if p.is_dir() and list(p.glob("segments*")):
                        index_path = p
                        break
            
            if index_path is None:
                raise FileNotFoundError(
                    f"Could not find Lucene index in {actual_extract_dir}. "
                    f"Expected to find 'segments*' files."
                )
            
            searcher = LuceneSearcher(str(index_path))
            print(f"✅ Loaded Pyserini index: {searcher.num_docs:,} documents")
            return searcher
        
        except ImportError:
            print("❌ Pyserini not installed, cannot load index")
            raise ImportError("Please install pyserini: pip install pyserini")
    
    elif config['type'] == 'pyserini_topics':
        # Load TREC topics and qrels from JSON files
        topics_file = extract_dir / "topics.json"
        qrels_file = extract_dir / "qrels.json"
        
        # Check if files exist in subdirectory
        if not topics_file.exists():
            subdir = list(extract_dir.glob("*"))[0]
            topics_file = subdir / "topics.json"
            qrels_file = subdir / "qrels.json"
        
        with open(topics_file, 'r') as f:
            topics = json.load(f)
        with open(qrels_file, 'r') as f:
            qrels = json.load(f)
        
        print(f"✅ Loaded {len(topics)} topics and {sum(len(docs) for docs in qrels.values())} qrel judgments")
        return topics, qrels
    
    else:
        raise ValueError(f"Unknown dataset type: {config['type']}")


# Convenience functions for specific datasets
def load_sherlock_holmes():
    """Load the Sherlock Holmes corpus as text."""
    return load_irtm_dataset("sherlock_holmes")


def load_conll2003():
    """Load the CoNLL-2003 NER dataset."""
    return load_irtm_dataset("conll2003")


def load_agentic_training_data():
    """Load all agentic training data JSON files."""
    return load_irtm_dataset("agentic_training_data")


def load_msmarco_index():
    """Load MS MARCO v1 passage index as Pyserini searcher."""
    return load_irtm_dataset("msmarco_v1_passage_index")


def load_trec_dl_2019():
    """Load TREC Deep Learning 2019 topics and qrels."""
    return load_irtm_dataset("trec_dl_2019")


if __name__ == "__main__":
    # Test the loader
    print("Testing IRTM Dataset Loader\n" + "="*60)
    
    # Test sherlock_holmes
    print("\n1. Testing sherlock_holmes...")
    text = load_sherlock_holmes()
    print(f"   Preview: {text[:100]}...")
    
    # Test conll2003
    print("\n2. Testing conll2003...")
    dataset = load_conll2003()
    print(f"   Splits: {dataset.keys()}")
    
    # Test agentic_training_data
    print("\n3. Testing agentic_training_data...")
    data = load_agentic_training_data()
    print(f"   Files loaded: {list(data.keys())[:5]}...")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
