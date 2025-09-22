# vLLM Deployment Guide for Knowledge Assistant

This document provides comprehensive instructions for deploying vLLM with Phi-3-mini model on Kubernetes to replace Ollama as the LLM backend for the Knowledge Assistant application.

## Overview

This deployment replaces the Ollama-based LLM service with vLLM, providing:
- **Better Performance**: Optimized inference engine for large language models
- **Scalability**: Kubernetes-native scaling and resource management
- **Reliability**: Production-ready deployment with health checks and monitoring
- **Cost Efficiency**: Better GPU utilization and resource management

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   vLLM Server   │
│   (Next.js)     │────│   (FastAPI)     │────│   (Phi-3-mini)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │   Vector Store  │
                       │   (Milvus)      │
                       └─────────────────┘
```

## Prerequisites

### 1. Kubernetes Cluster Requirements
- **Kubernetes Version**: 1.20 or higher
- **GPU Support**: NVIDIA GPU operator installed
- **Storage**: Persistent volume support
- **Ingress**: NGINX ingress controller

### 2. Hardware Requirements
- **GPU**: NVIDIA GPU with at least 8GB VRAM (Tesla T4, V100, A100, RTX 4090)
- **CPU**: 4+ cores recommended
- **Memory**: 16GB+ RAM recommended
- **Storage**: 50GB+ for model cache

### 3. Software Requirements
- `kubectl` configured and connected to cluster
- `docker` for building images (if needed)
- Access to NVIDIA GPU operator

## Deployment Steps

### Step 1: Prepare Kubernetes Cluster

1. **Verify GPU availability**:
   ```bash
   kubectl get nodes -o wide
   kubectl describe nodes | grep -i gpu
   ```

2. **Check NVIDIA GPU operator**:
   ```bash
   kubectl get pods -n gpu-operator
   ```

3. **Verify storage classes**:
   ```bash
   kubectl get storageclass
   ```

### Step 2: Deploy vLLM

1. **Navigate to k8s directory**:
   ```bash
   cd k8s
   ```

2. **Run deployment script**:
   ```bash
   ./deploy-vllm.sh
   ```

   Or deploy manually:
   ```bash
   kubectl apply -f vllm-pvc.yaml
   kubectl apply -f vllm-configmap.yaml
   kubectl apply -f vllm-deployment.yaml
   kubectl apply -f vllm-service.yaml
   kubectl apply -f vllm-ingress.yaml
   kubectl apply -f vllm-hpa.yaml
   ```

### Step 3: Verify Deployment

1. **Check pod status**:
   ```bash
   kubectl get pods -n knowledge-assistant
   ```

2. **Check services**:
   ```bash
   kubectl get services -n knowledge-assistant
   ```

3. **Check logs**:
   ```bash
   kubectl logs -n knowledge-assistant -l app=vllm-server
   ```

### Step 4: Test vLLM Service

1. **Health check**:
   ```bash
   kubectl port-forward -n knowledge-assistant svc/vllm-service 8000:8000
   curl http://localhost:8000/health
   ```

2. **List models**:
   ```bash
   curl http://localhost:8000/v1/models
   ```

3. **Test chat completion**:
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "phi-3-mini",
       "messages": [{"role": "user", "content": "Hello!"}],
       "temperature": 0.7,
       "max_tokens": 100
     }'
   ```

## Backend Configuration

### Step 1: Update Environment Variables

Create or update your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://vllm-service.knowledge-assistant.svc.cluster.local:8000
VLLM_MODEL=phi-3-mini
VLLM_API_KEY=

# LangChain Configuration
LANGCHAIN_LLM_PROVIDER=vllm
LANGCHAIN_LLM_MODEL=phi-3-mini
```

### Step 2: Update Backend Code

The backend has been updated to support vLLM:

1. **New vLLM Client**: `backend/langchain_services/llm_providers/vllm_client.py`
2. **Updated Configuration**: `backend/config.py`
3. **Updated Service**: `backend/services/langchain_rag_service.py`
4. **Updated Health Check**: `backend/routers/health.py`

### Step 3: Deploy Backend

1. **Build backend image**:
   ```bash
   cd backend
   docker build -t knowledge-assistant-backend:latest .
   ```

2. **Deploy to Kubernetes**:
   ```bash
   kubectl apply -f ../k8s/backend-deployment.yaml  # Create this if needed
   ```

## Configuration Details

### vLLM Configuration

The vLLM server is configured with:

```yaml
# Model Configuration
model: microsoft/Phi-3-mini-4k-instruct
max_model_length: 4096
dtype: auto
trust_remote_code: true

# Performance Configuration
tensor_parallel_size: 1
gpu_memory_utilization: 0.8
max_batch_size: 256
max_num_seqs: 256
```

### Resource Allocation

```yaml
resources:
  requests:
    memory: "8Gi"
    cpu: "2"
    nvidia.com/gpu: 1
  limits:
    memory: "16Gi"
    cpu: "4"
    nvidia.com/gpu: 1
```

### Scaling Configuration

```yaml
# Horizontal Pod Autoscaler
minReplicas: 1
maxReplicas: 3
cpuTarget: 70%
memoryTarget: 80%
```

## Monitoring and Troubleshooting

### Health Checks

1. **Pod Health**:
   ```bash
   kubectl get pods -n knowledge-assistant -l app=vllm-server
   ```

2. **Service Health**:
   ```bash
   curl http://<SERVICE_IP>:8000/health
   ```

3. **Backend Health**:
   ```bash
   curl http://<BACKEND_IP>/health
   ```

### Common Issues

#### 1. Pod Stuck in Pending
- **Cause**: Insufficient GPU resources
- **Solution**: Check GPU availability and node selectors

#### 2. Model Loading Failures
- **Cause**: Insufficient memory or storage
- **Solution**: Increase resource limits or storage size

#### 3. Slow Response Times
- **Cause**: High load or resource constraints
- **Solution**: Scale up replicas or increase resources

#### 4. Connection Refused
- **Cause**: Service not ready or network issues
- **Solution**: Check service status and network policies

### Log Analysis

```bash
# View logs
kubectl logs -n knowledge-assistant -l app=vllm-server

# Follow logs
kubectl logs -n knowledge-assistant -l app=vllm-server --follow

# Check events
kubectl get events -n knowledge-assistant --sort-by='.lastTimestamp'
```

## Performance Optimization

### 1. GPU Optimization
- Adjust `gpu_memory_utilization` based on your GPU
- Use tensor parallelism for multi-GPU setups
- Optimize batch sizes for your workload

### 2. Model Optimization
- Use appropriate model precision (fp16, bf16)
- Enable Flash Attention for better performance
- Optimize context length based on use case

### 3. Infrastructure Optimization
- Use fast storage for model cache
- Optimize network policies
- Implement proper resource limits

## Security Considerations

### 1. Network Security
- Implement network policies
- Use TLS for external access
- Restrict access to internal services

### 2. Authentication
- Add API key authentication
- Implement rate limiting
- Use RBAC for Kubernetes resources

### 3. Data Protection
- Encrypt data in transit
- Secure model storage
- Implement audit logging

## Backup and Recovery

### 1. Model Backup
```bash
# Backup model cache
kubectl exec -n knowledge-assistant <POD_NAME> -- tar -czf /tmp/model-backup.tar.gz /root/.cache
kubectl cp knowledge-assistant/<POD_NAME>:/tmp/model-backup.tar.gz ./model-backup.tar.gz
```

### 2. Configuration Backup
```bash
# Backup configurations
kubectl get configmap vllm-config -n knowledge-assistant -o yaml > vllm-config-backup.yaml
```

### 3. Recovery
```bash
# Restore configurations
kubectl apply -f vllm-config-backup.yaml
```

## Migration from Ollama

### Step 1: Prepare Migration
1. Backup current Ollama data
2. Test vLLM deployment
3. Update backend configuration

### Step 2: Switch Traffic
1. Update environment variables
2. Restart backend services
3. Verify functionality

### Step 3: Cleanup
1. Remove Ollama deployments
2. Clean up resources
3. Update documentation

## Cost Optimization

### 1. Resource Optimization
- Right-size resource requests
- Use spot instances for non-critical workloads
- Implement proper scaling policies

### 2. Model Optimization
- Use quantized models when possible
- Implement model caching
- Optimize inference parameters

### 3. Infrastructure Optimization
- Use appropriate instance types
- Implement auto-scaling
- Monitor and optimize costs

## Support and Maintenance

### Regular Maintenance
- Monitor resource usage
- Update model versions
- Apply security patches
- Backup configurations

### Troubleshooting Resources
- vLLM Documentation: https://docs.vllm.ai/
- Kubernetes Documentation: https://kubernetes.io/docs/
- NVIDIA GPU Operator: https://docs.nvidia.com/datacenter/cloud-native/

## Conclusion

This deployment provides a robust, scalable, and efficient LLM serving solution for the Knowledge Assistant application. The vLLM-based architecture offers better performance, reliability, and cost-effectiveness compared to the previous Ollama setup.

For additional support or questions, refer to the troubleshooting section or consult the Kubernetes and vLLM documentation.
