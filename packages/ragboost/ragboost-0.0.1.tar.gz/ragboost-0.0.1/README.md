# RAGBoost

## Getting Started 
### Install from Source
Python >=3.10
```bash
git clone https://github.com/SecretSettler/RAGBoost.git
cd RAGBoost
pip install -e .
```

### Using Docker
#### Docker Image
```
docker pull seanjiang01/prompt-planner:v0.0.1
docker run -d --gpus all --name prompt-planner-container prompt-planner
docker exec -it prompt-planner-container bash
```

#### Build from scatch
```
git clone https://github.com/SecretSettler/RAGBoost.git
cd RAGBoost
docker build -t ragboost .
docker run -d --gpus all --name ragboost-container ragboost
docker exec -it ragboost-container bash
```
**Note:** This is slow due to building FlashAttention from scatch.

## Quick usage
### Offline
#### Build dataset and index from scratch
----------------
**1. BM25, MultihopRAG**

RECOMMENDED: Please refer to `examples/construct_rag_data/multihopRAG_bm25.py`

Quick running command:
```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "xpack.security.http.ssl.enabled=false" \
  -e "xpack.security.transport.ssl.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.18.2

python examples/construct_rag_data/multihopRAG_bm25.py
```

**2. Faiss, MultihopRAG**

RECOMMENDED: Please refer to `examples/construct_rag_data/multihopRAG_faiss.py`

Quick running command:
```bash
python -m sglang.launch_server \
  --model-path Alibaba-NLP/gte-Qwen2-7B-instruct \
  --is-embedding \
  --host 0.0.0.0 \
  --port 30000

python examples/construct_rag_data/multihopRAG_faiss.py
```
------
#### Generating and selecting plan
RECOMMENDED: Please refer to `examples/planner/generate_plan.py`

Quick running command:
```
python examples/planner/generate_plan.py --prompts_path <PATH-TO-YOUR RETRIEVAL-OUTPUT> --output_path <YOUR-PLAN-SAVE-PATH>
```

#### Launch inference
RECOMMENDED: Please refer to `examples/planner/sglang_inference.py`

Quick running command:
```
python -m sglang.launch_server --model-path Qwen/Qwen3-32B --port 30000 --tp-size 4 --reasoning-parser qwen3 --enable-metrics --schedule-policy lpm

python examples/planner/sglang_inference.py --model Qwen/Qwen3-32B --plan_path <YOUR-PLAN-SAVE-PATH> --corpus_path <PATH-TO-YOUR-CORPUS-WITH-CTX-LENGTH>
```


## Data Format:
If you have your own data, please format to the example below. Currently we only support data with `jsonl` format. Each json should at least contain these attributes:
```json
{
    "qid": 0,
    "text": "Is the sky blue?",
    "answer": ["Yes", "Yes the sky is blue"],
    "top_k_doc_id": [2, 8, 1, 10]
}
```
This should be under the `--prompts_path` for plan generation and selection.

## Roadmap
- [x] Implement the Group Aware RR scheduler
- [ ] Support online inference
- [ ] Implement a faster prefix cache
- [ ] Support multi-modality models
