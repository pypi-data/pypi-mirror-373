"""
Monitoring Service
Performance monitoring and metrics collection
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from threading import Lock

from ...abstractions.base.service import BaseService

@dataclass
class Metric:
    """Performance metric"""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class MonitoringService(BaseService):
    """Performance monitoring service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.metrics: Dict[str, Metric] = {}
        self.completed: List[Metric] = []
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """Initialize the service"""
        self._logger.info("Initializing MonitoringService...")
        self.is_initialized = True
        return True
    
    def start_metric(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start performance metric"""
        
        with self._lock:
            metric_id = f"{name}_{int(time.time() * 1000)}"
            
            metric = Metric(
                name=name,
                start_time=time.time(),
                metadata=metadata or {}
            )
            
            self.metrics[metric_id] = metric
            return metric_id
    
    def end_metric(self, metric_id: str) -> Optional[float]:
        """End performance metric"""
        
        with self._lock:
            if metric_id not in self.metrics:
                return None
            
            metric = self.metrics[metric_id]
            metric.end_time = time.time()
            metric.duration = metric.end_time - metric.start_time
            
            self.completed.append(metric)
            del self.metrics[metric_id]
            
            return metric.duration
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        with self._lock:
            if not self.completed:
                return {"total_operations": 0}
            
            grouped = {}
            for metric in self.completed:
                if metric.name not in grouped:
                    grouped[metric.name] = []
                if metric.duration:
                    grouped[metric.name].append(metric.duration)
            
            summary = {"total_operations": len(self.completed)}
            
            for name, durations in grouped.items():
                if durations:
                    summary[name] = {
                        "count": len(durations),
                        "min": min(durations),
                        "max": max(durations),
                        "avg": sum(durations) / len(durations)
                    }
            
            return summary
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        with self._lock:
            self.metrics.clear()
            self.completed.clear()
    
    def shutdown(self) -> None:
        """Shutdown the service"""
        self._logger.info("Shutting down MonitoringService...")
        self.clear_metrics()
        self.is_initialized = False
