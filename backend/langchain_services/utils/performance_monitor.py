"""
Performance monitoring utilities for LangChain services
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor performance metrics for LangChain operations"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.end_time = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.metrics = {
            "start_time": datetime.utcnow().isoformat(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_info": psutil.virtual_memory()._asdict(),
            "operations": []
        }
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.time()
        if self.start_time:
            self.metrics["total_time"] = self.end_time - self.start_time
            self.metrics["end_time"] = datetime.utcnow().isoformat()
            self.metrics["final_cpu_percent"] = psutil.cpu_percent()
            self.metrics["final_memory_info"] = psutil.virtual_memory()._asdict()
    
    def add_operation(self, operation_name: str, duration: float, metadata: Dict[str, Any] = None):
        """Add an operation to the metrics"""
        operation = {
            "name": operation_name,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.metrics["operations"].append(operation)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics"""
        if not self.metrics.get("operations"):
            return {"error": "No operations recorded"}
        
        operations = self.metrics["operations"]
        total_time = self.metrics.get("total_time", 0)
        
        return {
            "total_operations": len(operations),
            "total_time": total_time,
            "average_operation_time": sum(op["duration"] for op in operations) / len(operations),
            "slowest_operation": max(operations, key=lambda x: x["duration"]),
            "fastest_operation": min(operations, key=lambda x: x["duration"]),
            "memory_usage": self.metrics.get("final_memory_info", {}),
            "cpu_usage": self.metrics.get("final_cpu_percent", 0)
        }

def monitor_performance(operation_name: str = None):
    """Decorator to monitor performance of functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance
                logger.info(f"Operation '{name}' completed in {duration:.2f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Operation '{name}' failed after {duration:.2f}s: {e}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance
                logger.info(f"Operation '{name}' completed in {duration:.2f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Operation '{name}' failed after {duration:.2f}s: {e}")
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ResourceMonitor:
    """Monitor system resources during operations"""
    
    def __init__(self):
        self.initial_cpu = psutil.cpu_percent()
        self.initial_memory = psutil.virtual_memory()
        self.peak_memory = 0
        self.peak_cpu = 0
    
    def start(self):
        """Start resource monitoring"""
        self.initial_cpu = psutil.cpu_percent()
        self.initial_memory = psutil.virtual_memory()
        self.peak_memory = self.initial_memory.used
        self.peak_cpu = self.initial_cpu
    
    def update(self):
        """Update resource usage"""
        current_cpu = psutil.cpu_percent()
        current_memory = psutil.virtual_memory()
        
        self.peak_cpu = max(self.peak_cpu, current_cpu)
        self.peak_memory = max(self.peak_memory, current_memory.used)
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        current_memory = psutil.virtual_memory()
        current_cpu = psutil.cpu_percent()
        
        return {
            "cpu": {
                "current": current_cpu,
                "peak": self.peak_cpu,
                "initial": self.initial_cpu
            },
            "memory": {
                "current": current_memory._asdict(),
                "peak_used": self.peak_memory,
                "initial": self.initial_memory._asdict()
            }
        }

class LatencyTracker:
    """Track latency for different operations"""
    
    def __init__(self):
        self.latencies = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.latencies[operation] = {
            "start_time": time.time(),
            "end_time": None,
            "duration": None
        }
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        if operation in self.latencies:
            end_time = time.time()
            start_time = self.latencies[operation]["start_time"]
            self.latencies[operation]["end_time"] = end_time
            self.latencies[operation]["duration"] = end_time - start_time
    
    def get_latency(self, operation: str) -> Optional[float]:
        """Get latency for an operation"""
        if operation in self.latencies and self.latencies[operation]["duration"] is not None:
            return self.latencies[operation]["duration"]
        return None
    
    def get_all_latencies(self) -> Dict[str, float]:
        """Get all recorded latencies"""
        return {
            op: data["duration"] 
            for op, data in self.latencies.items() 
            if data["duration"] is not None
        }

class ThroughputMonitor:
    """Monitor throughput for operations"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.operations = []
        self.start_time = None
    
    def start(self):
        """Start throughput monitoring"""
        self.start_time = time.time()
        self.operations = []
    
    def record_operation(self, operation_name: str = "operation"):
        """Record an operation"""
        self.operations.append({
            "name": operation_name,
            "timestamp": time.time()
        })
        
        # Keep only recent operations
        if len(self.operations) > self.window_size:
            self.operations = self.operations[-self.window_size:]
    
    def get_throughput(self) -> Dict[str, float]:
        """Get current throughput metrics"""
        if not self.operations or not self.start_time:
            return {"operations_per_second": 0.0, "total_operations": 0}
        
        current_time = time.time()
        total_time = current_time - self.start_time
        total_operations = len(self.operations)
        
        if total_time > 0:
            ops_per_second = total_operations / total_time
        else:
            ops_per_second = 0.0
        
        return {
            "operations_per_second": ops_per_second,
            "total_operations": total_operations,
            "total_time": total_time
        }

class PerformanceProfiler:
    """Comprehensive performance profiler"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.resource_monitor = ResourceMonitor()
        self.latency_tracker = LatencyTracker()
        self.throughput_monitor = ThroughputMonitor()
    
    def start_profiling(self):
        """Start comprehensive profiling"""
        self.monitor.start_monitoring()
        self.resource_monitor.start()
        self.throughput_monitor.start()
    
    def stop_profiling(self):
        """Stop comprehensive profiling"""
        self.monitor.stop_monitoring()
    
    def record_operation(self, operation_name: str, duration: float, metadata: Dict[str, Any] = None):
        """Record an operation"""
        self.monitor.add_operation(operation_name, duration, metadata)
        self.throughput_monitor.record_operation(operation_name)
        self.resource_monitor.update()
    
    def start_operation_timer(self, operation: str):
        """Start timing an operation"""
        self.latency_tracker.start_timer(operation)
    
    def end_operation_timer(self, operation: str):
        """End timing an operation"""
        self.latency_tracker.end_timer(operation)
        duration = self.latency_tracker.get_latency(operation)
        if duration is not None:
            self.record_operation(operation, duration)
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get a comprehensive performance report"""
        return {
            "performance_metrics": self.monitor.get_metrics(),
            "performance_summary": self.monitor.get_summary(),
            "resource_usage": self.resource_monitor.get_usage(),
            "latencies": self.latency_tracker.get_all_latencies(),
            "throughput": self.throughput_monitor.get_throughput()
        }
