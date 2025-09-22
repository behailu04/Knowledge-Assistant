#!/bin/bash

# Knowledge Assistant Kubernetes Deployment Script
# This script deploys the complete Knowledge Assistant stack using Kustomize

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Default values
ENVIRONMENT="dev"
NAMESPACE="knowledge-assistant-dev"
BUILD_IMAGES=true  # Always build images by default since they're required
SKIP_VLLM=false

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy (dev|prod) [default: dev]"
    echo "  -n, --namespace NS       Kubernetes namespace [default: knowledge-assistant-dev]"
    echo "  --no-build               Skip building Docker images (not recommended)"
    echo "  --skip-vllm              Skip vLLM deployment"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment dev"
    echo "  $0 --environment prod --namespace knowledge-assistant-prod"
    echo "  $0 --skip-vllm --no-build"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --no-build)
            BUILD_IMAGES=false
            shift
            ;;
        --skip-vllm)
            SKIP_VLLM=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be 'dev' or 'prod'"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if kustomize is available
if ! command -v kustomize &> /dev/null; then
    print_error "kustomize is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_header "Knowledge Assistant Kubernetes Deployment"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Build Images: $BUILD_IMAGES"
echo "Skip vLLM: $SKIP_VLLM"
echo ""

# Build images if requested
if [[ "$BUILD_IMAGES" == "true" ]]; then
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH. Cannot build images."
        exit 1
    fi
    
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    if ! docker build --platform linux/amd64 -f ./backend/Dockerfile -t knowledge-assistant-backend:latest .; then
        print_error "Failed to build backend image"
        exit 1
    fi
    
    # Build frontend image
    print_status "Building frontend image..."
    if ! docker build --platform linux/amd64 -f ./frontend/Dockerfile -t knowledge-assistant-frontend:latest .; then
        print_error "Failed to build frontend image"
        exit 1
    fi
    
    print_status "Docker images built successfully!"
fi

# Create namespace if it doesn't exist
print_status "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Kustomize
print_status "Deploying Knowledge Assistant stack..."

if [[ "$SKIP_VLLM" == "true" ]]; then
    print_warning "Skipping vLLM deployment"
    # Deploy without vLLM
    kustomize build overlays/$ENVIRONMENT | kubectl apply -f -
else
    # Deploy with vLLM
    kustomize build overlays/$ENVIRONMENT | kubectl apply -f -
fi

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."

# Wait for database services first
print_status "Waiting for PostgreSQL..."
kubectl wait --for=condition=Available deployment/postgres -n $NAMESPACE --timeout=300s

print_status "Waiting for Redis..."
kubectl wait --for=condition=Available deployment/redis -n $NAMESPACE --timeout=300s

# Wait for Milvus services
print_status "Waiting for Milvus dependencies..."
kubectl wait --for=condition=Available deployment/etcd -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=Available deployment/minio -n $NAMESPACE --timeout=300s

print_status "Waiting for Milvus..."
kubectl wait --for=condition=Available deployment/milvus -n $NAMESPACE --timeout=300s

print_status "Waiting for Attu..."
kubectl wait --for=condition=Available deployment/attu -n $NAMESPACE --timeout=300s

# Wait for vLLM if not skipped
if [[ "$SKIP_VLLM" == "false" ]]; then
    print_status "Waiting for vLLM..."
    kubectl wait --for=condition=Available deployment/vllm-server -n $NAMESPACE --timeout=600s
fi

# Wait for backend
print_status "Waiting for Backend API..."
kubectl wait --for=condition=Available deployment/backend -n $NAMESPACE --timeout=300s

# Wait for frontend
print_status "Waiting for Frontend..."
kubectl wait --for=condition=Available deployment/frontend -n $NAMESPACE --timeout=300s

# Get service information
print_status "Getting service information..."
SERVICES=$(kubectl get services -n $NAMESPACE -o wide)

echo ""
print_header "Deployment Summary"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo ""

print_status "Services deployed:"
kubectl get services -n $NAMESPACE

echo ""
print_status "Pods status:"
kubectl get pods -n $NAMESPACE

echo ""
print_status "Ingress information:"
kubectl get ingress -n $NAMESPACE

echo ""
print_header "Access Information"
echo "To access the application:"
echo "1. Add the following to your /etc/hosts file:"
echo "   <INGRESS_IP> knowledge-assistant.local"
echo ""
echo "2. Access the services:"
echo "   Frontend: http://knowledge-assistant.local"
echo "   Backend API: http://knowledge-assistant.local/api"
echo "   vLLM API: http://knowledge-assistant.local/vllm"
echo "   Milvus Attu: http://knowledge-assistant.local/attu"
echo ""

print_status "Deployment completed successfully!"
echo ""
echo "To check logs:"
echo "  kubectl logs -n $NAMESPACE -l app=backend"
echo "  kubectl logs -n $NAMESPACE -l app=frontend"
echo "  kubectl logs -n $NAMESPACE -l app=vllm-server"
echo ""
echo "To scale services:"
echo "  kubectl scale deployment backend -n $NAMESPACE --replicas=3"
echo "  kubectl scale deployment frontend -n $NAMESPACE --replicas=3"
echo ""
echo "To delete deployment:"
echo "  kubectl delete namespace $NAMESPACE"
