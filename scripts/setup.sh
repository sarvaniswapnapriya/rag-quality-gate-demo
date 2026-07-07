#!/bin/bash
# scripts/setup.sh
# Quick setup script for RAG Quality Gate demo

set -e

echo "🚀 RAG Quality Gate Demo - Setup Script"
echo "========================================"
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Install it first."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ helm not found. Install it first."
    exit 1
fi

echo "✓ kubectl and helm found"
echo ""

# Check K8s cluster
echo "✓ Checking Kubernetes cluster..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not running"
    echo "   Mac: Docker Desktop → Settings → Kubernetes → Enable"
    echo "   Linux: minikube start --cpus 4 --memory 8192"
    exit 1
fi
echo "✓ K8s cluster is running"
echo ""

# Ask for Gemini API key
echo "📝 Enter your Gemini API Key (from https://aistudio.google.com/app/apikeys):"
read -s GEMINI_KEY
echo ""

if [ -z "$GEMINI_KEY" ]; then
    echo "❌ API key cannot be empty"
    exit 1
fi

# Update .env
echo "🔧 Updating .env file..."
cat > .env << EOF
GOOGLE_API_KEY=$GEMINI_KEY
GITHUB_TOKEN=your-github-token-here
EOF
echo "✓ .env created (add GITHUB_TOKEN manually if needed)"
echo ""

# Check if Testkube is installed
echo "✓ Checking Testkube installation..."
if ! kubectl get namespace testkube &> /dev/null; then
    echo "📦 Installing Testkube..."
    kubectl create namespace testkube
    helm repo add testkube https://kubeshop.github.io/helm-charts
    helm repo update
    helm install testkube testkube/testkube -n testkube --create-namespace
    echo "✓ Testkube installed"
else
    echo "✓ Testkube namespace already exists"
fi
echo ""

# Create K8s secret
echo "🔐 Creating Kubernetes secret..."
kubectl delete secret gemini-secrets -n testkube 2>/dev/null || true
kubectl create secret generic gemini-secrets \
  --from-literal=api-key=$GEMINI_KEY \
  -n testkube
echo "✓ Secret created"
echo ""

# Deploy TestWorkflow
echo "📋 Deploying TestWorkflow..."
kubectl apply -f .testkube/rag-quality-gate.yaml -n testkube
echo "✓ TestWorkflow deployed"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update GitHub repo URL in .testkube/rag-quality-gate.yaml"
echo "2. Add GitHub secrets:"
echo "   - TK_ORG_ID"
echo "   - TK_ENV_ID"
echo "   - TK_API_TOKEN"
echo "3. Push to GitHub: git push origin main"
echo "4. Watch in: GitHub Actions or Testkube Dashboard"
echo ""
echo "Test locally (optional):"
echo "  pip install -r requirements.txt"
echo "  pytest tests/test_rag_eval.py -v"
