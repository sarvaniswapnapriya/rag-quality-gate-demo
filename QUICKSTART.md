# QUICKSTART - Do This First

## You Have 5 Minutes? Do This:

```bash
# 1. Get Gemini key (2 min)
# → Go to: https://aistudio.google.com/app/apikeys
# → Click "Create API Key"
# → Copy the key

# 2. Enable K8s (if not running)
# Mac: Docker Desktop → Settings → Kubernetes → Enable (3 min)
# Linux: minikube start --cpus 4 --memory 8192 (3 min)
# Cloud: Use your existing cluster

# 3. Run setup script (auto-installs everything)
bash scripts/setup.sh
# → Paste your Gemini key when prompted
```

## Done ✅

Your TestWorkflow is now deployed. Now:

1. **Update GitHub repo URL** in `.testkube/rag-quality-gate.yaml` (line 11)
   ```yaml
   uri: https://github.com/YOUR-ORG/rag-quality-gate-demo
   ```

2. **Get Testkube credentials** from your Testkube Dashboard
   - Organization ID
   - Environment ID
   - API Token

3. **Add secrets to GitHub** (Settings → Secrets → Actions)
   - `TK_ORG_ID`
   - `TK_ENV_ID`
   - `TK_API_TOKEN`

4. **Push to GitHub**
   ```bash
   git add .
   git commit -m "initial: RAG quality gate"
   git push origin main
   ```

5. **Watch it run**
   - GitHub Actions tab → see workflow run
   - OR Testkube Dashboard → Test Workflows

---

## Want to Test Locally First?

```bash
# Install Python deps
pip install -r requirements.txt

# Run tests
export GOOGLE_API_KEY=your-key-here
pytest tests/test_rag_eval.py -v

# Should see: 20 tests, some pass/fail depending on setup
```

---

## Customize Later

### Add your docs:
`src/rag/rag_pipeline.py` → `_load_knowledge_base()`

### Add test questions:
`tests/fixtures/rag_test_cases.yml` → add more Q&A pairs

### Change prompts:
`src/rag/prompts.py` → edit `BASELINE_PROMPT` or `CANDIDATE_PROMPT`

---

## That's It 🎉

Everything else is configured and ready to go.
