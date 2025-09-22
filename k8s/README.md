# vLLM Kubernetes Deployment for Knowledge Assistant

This directory contains Kubernetes manifests and deployment scripts for deploying vLLM with Phi-3-mini model to serve as the LLM backend for the Knowledge Assistant application.

## Overview

The deployment includes:
- vLLM server with Phi-3-mini-4k-instruct model
- Kubernetes services for internal and external access
- Persistent volume for model caching
- Horizontal Pod Autoscaler (HPA) for scaling
- Ingress configuration for external access
- Health checks and monitoring

## Prerequisites

1. **Kubernetes Cluster**: A Kubernetes cluster with GPU support
2. **GPU Nodes**: Nodes with NVIDIA GPUs (Tesla T4, V100, A100, or RTX 4090)
3. **NVIDIA GPU Operator**: For GPU resource management
4. **Storage Class**: A storage class named `fast-ssd` (modify in `vllm-pvc.yaml` if different)
5. **Ingress Controller**: NGINX ingress controller for external access

## Files Description

### Core Deployment Files
- `vllm-deployment.yaml`: Main deployment manifest for vLLM server
- `vllm-service.yaml`: Kubernetes services (ClusterIP and LoadBalancer)
- `vllm-pvc.yaml`: PersistentVolumeClaim for model caching and namespace
- `vllm-ingress.yaml`: Ingress configuration for external access
- `vllm-configmap.yaml`: Configuration maps for vLLM and Phi model
- `vllm-hpa.yaml`: Horizontal Pod Autoscaler configuration

### Deployment Script
- `deploy-vllm.sh`: Automated deployment script

## Quick Deployment

1. **Deploy vLLM**:
   ```bash
   cd k8s
   ./deploy-vllm.sh
   ```

2. **Verify Deployment**:
   ```bash
   kubectl get pods -n knowledge-assistant
   kubectl get services -n knowledge-assistant
   kubectl get ingress -n knowledge-assistant
   ```

3. **Check Logs**:
   ```bash
   kubectl logs -n knowledge-assistant -l app=vllm-server
   ```

## Manual Deployment

If you prefer to deploy manually:

```bash
# Create namespace and PVC
kubectl apply -f vllm-pvc.yaml

# Create ConfigMap
kubectl apply -f vllm-configmap.yaml

# Deploy vLLM server
kubectl apply -f vllm-deployment.yaml

# Create services
kubectl apply -f vllm-service.yaml

# Create ingress
kubectl apply -f vllm-ingress.yaml

# Create HPA
kubectl apply -f vllm-hpa.yaml
```

## Configuration

### Model Configuration
The Phi-3-mini-4k-instruct model is configured with:
- Max model length: 4096 tokens
- GPU memory utilization: 80%
- Tensor parallel size: 1
- Auto data type detection

### Resource Requirements
- **CPU**: 2 cores (request), 4 cores (limit)
- **Memory**: 8Gi (request), 16Gi (limit)
- **GPU**: 1 NVIDIA GPU
- **Storage**: 50Gi for model cache

### Scaling Configuration
- **Min Replicas**: 1
- **Max Replicas**: 3
- **CPU Target**: 70% utilization
- **Memory Target**: 80% utilization

## Accessing the Service

### Internal Access
From within the cluster:
```bash
curl http://vllm-service.knowledge-assistant.svc.cluster.local:8000/health
curl http://vllm-service.knowledge-assistant.svc.cluster.local:8000/v1/models
```

### External Access
1. **LoadBalancer Service**:
   ```bash
   kubectl get service vllm-service-external -n knowledge-assistant
   ```

2. **Ingress** (if configured):
   - Add entries to `/etc/hosts`:
     ```
     <INGRESS_IP> vllm.knowledge-assistant.local
     <INGRESS_IP> vllm-api.knowledge-assistant.local
     ```
   - Access via:
     ```bash
     curl http://vllm.knowledge-assistant.local/health
     curl http://vllm-api.knowledge-assistant.local/v1/models
     ```

## Testing the API

### Health Check
```bash
curl http://<SERVICE_IP>:8000/health
```

### List Models
```bash
curl http://<SERVICE_IP>:8000/v1/models
```

### Chat Completion
```bash
curl -X POST http://<SERVICE_IP>:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-3-mini",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

## Backend Integration

The Knowledge Assistant backend has been configured to use vLLM instead of Ollama:

### Configuration Changes
- `LLM_PROVIDER`: Set to `"vllm"`
- `VLLM_BASE_URL`: Set to internal service URL
- `VLLM_MODEL`: Set to `"phi-3-mini"`

### Environment Variables
```bash
export LLM_PROVIDER=vllm
export VLLM_BASE_URL=http://vllm-service.knowledge-assistant.svc.cluster.local:8000
export VLLM_MODEL=phi-3-mini
```

## Monitoring and Troubleshooting

### Check Pod Status
```bash
kubectl get pods -n knowledge-assistant -l app=vllm-server
kubectl describe pod <POD_NAME> -n knowledge-assistant
```

### Check Logs
```bash
kubectl logs -n knowledge-assistant -l app=vllm-server
kubectl logs -n knowledge-assistant -l app=vllm-server --follow
```

### Check Resource Usage
```bash
kubectl top pods -n knowledge-assistant
kubectl top nodes
```

### Check Events
```bash
kubectl get events -n knowledge-assistant --sort-by='.lastTimestamp'
```

## Scaling

### Manual Scaling
```bash
kubectl scale deployment vllm-server -n knowledge-assistant --replicas=2
```

### Automatic Scaling
The HPA will automatically scale based on CPU and memory usage:
```bash
kubectl get hpa -n knowledge-assistant
kubectl describe hpa vllm-hpa -n knowledge-assistant
```

## Cleanup

To remove the vLLM deployment:

```bash
kubectl delete -f vllm-hpa.yaml
kubectl delete -f vllm-ingress.yaml
kubectl delete -f vllm-service.yaml
kubectl delete -f vllm-deployment.yaml
kubectl delete -f vllm-configmap.yaml
kubectl delete -f vllm-pvc.yaml
```

Or delete the entire namespace:
```bash
kubectl delete namespace knowledge-assistant
```

## Customization

### Different Model
To use a different model, modify:
1. `MODEL_NAME` environment variable in `vllm-deployment.yaml`
2. `--model` argument in deployment
3. `VLLM_MODEL` in backend configuration

### Resource Adjustments
Modify resource requests/limits in `vllm-deployment.yaml` based on your hardware.

### Storage Configuration
Update `storageClassName` in `vllm-pvc.yaml` to match your cluster's storage classes.

## Security Considerations

1. **Network Policies**: Consider implementing network policies to restrict access
2. **Authentication**: Add API key authentication for production use
3. **TLS**: Enable TLS for external access
4. **Resource Limits**: Ensure proper resource limits to prevent resource exhaustion

## Performance Optimization

1. **GPU Memory**: Adjust `--gpu-memory-utilization` based on your GPU
2. **Batch Size**: Modify `--max-batch-size` for throughput optimization
3. **Model Length**: Adjust `--max-model-len` based on your use case
4. **Tensor Parallelism**: Increase `--tensor-parallel-size` for multi-GPU setups
