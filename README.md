# Chatbot BD Embassy Berlin

<p align="center">
  <img src="reports/Geomatry report.png" width="600" alt="Dashboard Geometry Model Graph"><br>
</p>

## How to run (parser)

### 1. Create & activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the parser

```bash
python -m parser.scripts.run \
  --start-url https://berlin.mofa.gov.bd/ \
  --max-pages 0 \
  --out parser/data/clean/output.cleaned.json
```

### 4. For faiss

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
