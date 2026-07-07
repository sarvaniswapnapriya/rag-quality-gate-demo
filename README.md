# RAG Quality Gate Demo

Automated quality gates for RAG pipelines using **Testkube**, **DeepEval**, and **Gemini API**.

## What This Does

```
git push (RAG code change)
    ↓
GitHub Action triggered
    ↓
Testkube runs 20 automated tests
    ↓
DeepEval metrics: Faithfulness, Recall, Relevancy
    ↓
Pass ✅ or Fail ❌ (blocks merge if quality degrades)
```

## What You Need

- ✅ **Gemini API Key** (free tier: 60 requests/min)
- ✅ **Kubernetes Cluster** (minikube, Docker Desktop, or cloud)
- ✅ **Testkube Installed** (open source, free)
- ✅ **GitHub Repo** (create one from this)

## Quick Start (15 Minutes)

### Step 1: Kubernetes + Testkube Setup

```bash
# Check if K8s is running
kubectl cluster-info

# If not running:
# - Mac: Docker Desktop → Settings → Kubernetes → Enable
# - Linux: minikube start --cpus 4 --memory 8192
# - Cloud: Use your existing cluster

# Install Testkube
helm repo add testkube https://kubeshop.github.io/helm-charts
helm repo update
helm install testkube testkube/testkube -n testkube --create-namespace

# Verify
kubectl get pods -n testkube
```

### Step 2: Get Gemini API Key

```bash
# Go to: https://aistudio.google.com/app/apikeys
# Click "Create API Key"
# Copy the key
# Save it securely (never commit it)
```

### Step 3: Clone & Setup This Repo

```bash
git clone <this-repo>
cd rag-quality-gate-demo

# Copy the example env file
cp .env.example .env

# Edit .env and paste your Gemini key
nano .env
# GOOGLE_API_KEY=your-key-here

# Install Python deps (optional, for local testing)
pip install -r requirements.txt
```

### Step 4: Create Kubernetes Secret

```bash
# Replace YOUR_GEMINI_KEY with your actual key
kubectl create secret generic gemini-secrets \
  --from-literal=api-key=YOUR_GEMINI_KEY \
  -n testkube
```

### Step 5: Deploy TestWorkflow

```bash
# Update the repo URL in .testkube/rag-quality-gate.yaml first:
# Replace "https://github.com/your-org/rag-quality-gate-demo"
# with your actual GitHub repo URL

kubectl apply -f .testkube/rag-quality-gate.yaml -n testkube

# Verify
kubectl get testworkflows -n testkube
```

### Step 6: Add GitHub Action Secrets

1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add 3 secrets (get values from Testkube Dashboard):
   - `TK_ORG_ID` (your org ID)
   - `TK_ENV_ID` (your environment ID)
   - `TK_API_TOKEN` (API token)

### Step 7: Push & Watch

```bash
git add .
git commit -m "initial: RAG quality gate setup"
git push origin main

# Watch it run:
# Option 1: GitHub Actions tab
# Option 2: Testkube Dashboard → Test Workflows → rag-quality-gate
```

## Testing Locally (Optional)

```bash
# Install deps
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY=your-key-here

# Run tests
pytest tests/test_rag_eval.py -v

# Expected: 20 tests, should pass or fail depending on prompts
```

## Customization

### Add Your Documents

Edit `src/rag/rag_pipeline.py` → `_load_knowledge_base()`:

```python
def _load_knowledge_base() -> list[str]:
    return [
        "Your company's refund policy...",
        "Your shipping terms...",
        "Your FAQs...",
    ]
```

### Add More Test Cases

Edit `tests/fixtures/rag_test_cases.yml`:

```yaml
- id: "qa_021"
  query: "Your question here"
  expected_answer: "Expected answer here"
  retrieval_context:
    - "Relevant document excerpt"
  category: "category_name"
```

### Change Thresholds

Edit `tests/test_rag_eval.py`:

```python
metrics = [
    FaithfulnessMetric(threshold=0.80),      # Change these
    ContextualRecallMetric(threshold=0.75),  # numbers
    AnswerRelevancyMetric(threshold=0.80),
]
```

## Quality Metrics Explained

| Metric | What It Tests | Threshold |
|--------|---|---|
| **Faithfulness** | Does answer hallucinate? | > 0.80 |
| **Contextual Recall** | Did retriever find relevant docs? | > 0.75 |
| **Answer Relevancy** | Is answer relevant to question? | > 0.80 |

If ANY metric fails → test fails → merge is blocked

## Troubleshooting

### Tests fail with "API key error"

```bash
# Check secret was created
kubectl get secrets -n testkube

# Verify secret has the key
kubectl get secret gemini-secrets -n testkube -o yaml

# Recreate if needed
kubectl delete secret gemini-secrets -n testkube
kubectl create secret generic gemini-secrets \
  --from-literal=api-key=YOUR_KEY \
  -n testkube
```

### Tests won't run

```bash
# Check TestWorkflow status
kubectl describe testworkflow rag-quality-gate -n testkube

# Check Testkube agent
kubectl get pods -n testkube | grep agent

# Check logs
kubectl logs -n testkube -l app=testkube-api -f
```

### GitHub Action won't trigger

```bash
# Verify secrets were added
# Settings → Secrets → Check TK_ORG_ID, TK_ENV_ID, TK_API_TOKEN

# Manual trigger for testing
testkube run testworkflow rag-quality-gate -n testkube --watch
```

## File Structure

```
rag-quality-gate-demo/
├── .github/workflows/rag-gate.yml      # GitHub Action trigger
├── .testkube/rag-quality-gate.yaml     # TestWorkflow definition
├── src/rag/
│   ├── __init__.py
│   ├── rag_pipeline.py                 # RAG system (uses Gemini)
│   └── prompts.py                      # System prompts
├── tests/
│   ├── test_rag_eval.py                # DeepEval test suite
│   └── fixtures/rag_test_cases.yml     # Q&A test cases
├── requirements.txt
├── .env.example                         # Copy to .env
├── .gitignore
└── README.md
```

## Flow Diagram

```
Engineer edits src/rag/prompts.py (system prompt)
         ↓ (git push)
GitHub Action fires (.github/workflows/rag-gate.yml)
         ↓
Testkube receives: "run rag-quality-gate workflow"
         ↓
K8s Pod starts (python:3.11 image)
         ↓
Pod: git clone → pip install → pytest tests/
         ↓
DeepEval runs 20 test cases (calls Gemini 80 times)
         ↓
Results: Faithfulness=0.95, Recall=0.88, Relevancy=0.92
         ↓
Assertions pass → test-results.json saved to artifacts
         ↓
GitHub shows ✅ green check (safe to merge)
```

## Costs

| Component | Cost |
|-----------|------|
| Gemini API (free tier) | $0 |
| Testkube (open source) | $0 |
| GitHub (public repo) | $0 |
| Kubernetes (self-hosted) | $0 or your existing cost |
| **Total** | **$0** |

## Next Steps

1. ✅ Get Gemini API key
2. ✅ Install Testkube in your K8s cluster
3. ✅ Clone this repo
4. ✅ Create K8s secret with your API key
5. ✅ Deploy TestWorkflow
6. ✅ Add GitHub Action secrets
7. ✅ Push to GitHub and watch it run

## Support

- Testkube Docs: https://docs.testkube.io/
- DeepEval Docs: https://deepeval.com/
- Gemini Docs: https://ai.google.dev/

---

**Made with ❤️ for RAG quality assurance**
