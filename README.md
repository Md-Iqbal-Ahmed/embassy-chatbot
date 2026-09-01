# RAG Chatbot Embassy Berlin

## 🌐 Multilingual Query Demonstrations

The system handles inquiries seamlessly across English, Bengali, and German.

### 1. Passport Inquiries
| Bengali Query | English Query |
| :---: | :---: |
| <img src="report/Outputs/Output 1.png" width="500" alt="Passport Fee Query in Bengali"/> | <img src="report/Outputs/Output 2.png" width="500" alt="Passport Fee Query in English"/> |
| *পাসপোর্ট ফি সংক্রান্ত তথ্য* | *E-Passport fee details* |

### 2. Consular Staff & Embassy Leadership
| German Query | English Query | Bengali Query |
| :---: | :---: | :---: |
| <img src="report/Outputs/Output 3.png" width="350" alt="Embassy Head Query in German"/> | <img src="report/Outputs/Output 4.png" width="350" alt="Embassy Head Query in English"/> | <img src="report/Outputs/Output 5.png" width="350" alt="Embassy Head Query in Bengali"/> |
| *Botschaftsleiter Anfrage* | *Head of Embassy inquiry* | *দূতাবাস প্রধানের তথ্য* |


## 📸 Demo Screenshots

<details>
<summary><b>🇧🇩 Bengali Queries (বাংলা প্রশ্ন ও উত্তর)</b></summary>
<br>

![Bengali Passport Info](report/Outputs/Output%201.png)
![Bengali Embassy Head Info](report/Outputs/Output%205.png)

</details>

<details>
<summary><b>🇬🇧 English Queries</b></summary>
<br>

![English Passport Info](report/Outputs/Output%202.png)
![English Embassy Head Info](report/Outputs/Output%204.png)

</details>

<details>
<summary><b>🇩🇪 German Queries (Deutsche Anfragen)</b></summary>
<br>

![German Embassy Head Info](report/Outputs/Output%203.png)

</details>


An end-to-end **Retrieval-Augmented Generation (RAG)** chatbot designed to assist users with consular service inquiries (e.g., passports, visas, dual nationality certificates, attestation, and fees) for an Embassy.

---

## 📌 Project Overview

Navigating consular instructions and complex web pages can be challenging. This project addresses that problem by:
- Scraping and cleaning data directly from the official embassy portal.
- Converting consular text into dense vector embeddings using multilingual models (OpenAI / Cohere).
- Leveraging **FAISS** for millisecond-latency vector similarity retrieval.
- Using an LLM through an interactive **Streamlit** user interface to provide grounded, hallucination-free answers.

---

## 🚀 Key Features

* **Query Support**: Accepts and processes inquiries in English.
* **Automated Data Processing**: Scrapes, extracts, cleans, and standardizes web content into clean JSON documents.
* **Semantic Text Chunking**: Splits large documents into overlapping token chunks to preserve context boundaries.
* **Dual Embedding Backend**: Built-in support for both **OpenAI** and **Cohere** multilingual embeddings.
* **Fast Vector Indexing**: Serializes and queries dense vector representations using Facebook AI Similarity Search (**FAISS**).
* **Interactive Streamlit UI**: User-friendly chat interface with streaming responses and contextual verification.

---

## 🏗️ System Architecture & Workflow

```text
[ Embassy Web Pages ]
          │
          ▼
   1. Ingestion & Cleaning (`parser/`)
          │  Extracts text & strips HTML boilerplate -> `output.cleaned.json`
          ▼
   2. Semantic Chunking (`retrieval/src/text_chunker.py`)
          │  Divides text into overlapping contextual blocks
          ▼
   3. Embedding & Indexing (`retrieval/src/build_multilingual_faiss.py`)
          │  Generates vector embeddings (Cohere / OpenAI) -> saves to FAISS
          ▼
   4. Query & RAG Generation (`streamlit/chatbot_mul.py`)
             Embeds user query -> searches FAISS -> injects context -> streams LLM answer
```
## 📁 Repository Structure


```text
Chatbot_BD_Embassy_Berlin/
├── parser/                                # Data Scraping & Preprocessing Pipeline
│   ├── src/
│   │   ├── crawler.py                     # Scrapes web pages from the official embassy portal
│   │   ├── cleaner.py                     # Strips HTML boilerplate and extracts clean text
│   │   └── utils.py                       # File I/O and JSON data utility functions
│   ├── scripts/
│   │   └── run.py                         # Automation script to trigger scraping and cleaning
│   └── data/
│       ├── clean/
│       │   └── output.cleaned.json        # Cleaned dataset structured with URLs, titles, and text
│       └── vector/                        # Stored vector files, embeddings, and FAISS indices
│           ├── cohere/                    # Cohere index files (.index, .npy, meta.json)
│           └── openai/                    # OpenAI index files (.index, .npy, meta.json)
├── retrieval/                             # Chunking, Embedding & Indexing Pipeline
│   └── src/
│       ├── text_chunker.py                # Splits cleaned documents into semantic chunks with overlap
│       ├── multilingual_embeddings.py     # Generates vector embeddings (OpenAI / Cohere)
│       ├── faiss_index.py                 # Wrapper for FAISS index creation and nearest-neighbor search
│       ├── build_multilingual_faiss.py    # Main builder script to index documents
│       └── search_multilingual_faiss.py   # CLI tool to test and verify similarity search
├── streamlit/                             # User Interface & RAG Query Pipeline
│   ├── chatbot_mul.py                     # Streamlit application entry point and chat handler
│   ├── embeddings_handler.py              # Loads and caches precomputed vector embeddings
│   ├── embeddings_cohere.pkl              # Pickled Cohere embeddings cache
│   ├── embeddings_openai.pkl              # Pickled OpenAI embeddings cache
│   ├── temp_context.txt                   # Buffer for holding retrieved context passages
│   └── .streamlit/
│       └── secrets.toml                   # API keys and secret configuration
├── requirements.txt                       # Python dependencies
└── README.md                              # Project documentation
### 2. Install dependencies


```
## 🛠️ Tech Stack & Dependencies

* **Language**: Python 3.10+
* **Frontend / UI**: Streamlit
* **Vector Search Engine**: FAISS (`faiss-cpu`)
* **Embedding Providers**: OpenAI Embeddings (`text-embedding-3-small`) & Cohere Multilingual Embeddings (`embed-multilingual-v3.0`)
* **Large Language Models (LLM)**: OpenAI API (`gpt-4o` / `gpt-3.5-turbo`)
* **Web Scraping & HTML Cleaning**: BeautifulSoup4 (`bs4`), Requests
* **Data Processing & Serialization**: NumPy, Pickle

---

## ⚙️ Module Responsibilities

* **`parser/src/crawler.py`**: Discovers and downloads HTML content across consular service categories from the official Bangladesh Embassy Berlin website.
* **`parser/src/cleaner.py`**: Extracts text from raw HTML, removes headers, footers, scripts, and navigation menus, and standardizes data into structured JSON entries.
* **`parser/scripts/run.py`**: Orchestrates the automated scraping and cleaning workflow to produce `output.cleaned.json`.
* **`retrieval/src/text_chunker.py`**: Splits cleaned documents into fixed-size semantic chunks with overlap to maintain contextual integrity across document splits.
* **`retrieval/src/multilingual_embeddings.py`**: Connects to the OpenAI and Cohere APIs to generate high-dimensional vector representations for multilingual text.
* **`retrieval/src/faiss_index.py`**: Provides helper methods to initialize, populate, save, and query dense FAISS similarity indices.
* **`retrieval/src/build_multilingual_faiss.py`**: Main indexing pipeline script that processes `output.cleaned.json`, computes embeddings, and serializes the index and metadata to disk.
* **`retrieval/src/search_multilingual_faiss.py`**: Command-line verification tool to test top-$k$ nearest-neighbor retrieval quality.
* **`streamlit/chatbot_mul.py`**: Primary web application entry point managing chat history, query embedding, FAISS similarity search, prompt augmentation, and response streaming.
* **`streamlit/embeddings_handler.py`**: Loads and caches vector indices and metadata into Streamlit memory to ensure low-latency query handling.

## How to run (parser)
```bash
pip install -r requirements.txt
```
### 1. Create & activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### 2. Run the parser

```bash
python -m parser.scripts.run \
  --start-url https://berlin.mofa.gov.bd/ \
  --max-pages 0 \
  --out parser/data/clean/output.cleaned.json
```

### 3. For faiss

```bash
python -m retrieval.src.build_faiss \
  --in parser/data/clean/output.cleaned.json \
  --index-out parser/data/vector/faiss_l2.index \
  --meta-out  parser/data/vector/meta.json \
  --index-type flat_l2 \
  --max-chars 900 --overlap 150 \
  --model paraphrase-multilingual-MiniLM-L12-v2
```

### 4. For query

```bash
python -m retrieval.src.search_faiss \
  --index parser/data/vector/faiss_l2.index \
  --meta  parser/data/vector/meta.json \
  --model paraphrase-multilingual-MiniLM-L12-v2 \
  --query "Address of Embassy" \
  --top-k 1 \
  --collapse url
```

- start-url → the seed URL (starting point for crawling).
- max-pages → 0 = crawl all pages in the domain (set a number to limit).
- out → file path where the cleaned JSON will be saved.
