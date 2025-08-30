"""Adaptive scheduler for orchestrating multi-scale PCE operations."""

import logging
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """A task to be executed by the scheduler."""
    id: str
    name: str
    function: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher values = higher priority
    dependencies: List[str] = field(default_factory=list)
    level: str = "L0"
    estimated_time: float = 1.0  # seconds
    max_retries: int = 3
    retry_count: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None


class TaskScheduler(ABC):
    """Abstract base class for task schedulers."""
    
    @abstractmethod
    def schedule(self, task: ScheduledTask) -> None:
        """Schedule a task for execution."""
        pass
    
    @abstractmethod
    def execute(self) -> None:
        """Execute scheduled tasks."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        pass


class AdaptiveScheduler(TaskScheduler):
    """Adaptive scheduler with entropy-based compute allocation."""
    
    def __init__(
        self,
        max_workers: int = 4,
        max_queue_size: int = 1000,
        entropy_threshold: float = 0.1,
        zoom_factor: float = 2.0
    ) -> None:
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.entropy_threshold = entropy_threshold
        self.zoom_factor = zoom_factor
        
        # Task management
        self.task_queue: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, Future] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.failed_tasks: Dict[str, ScheduledTask] = {}
        
        # Level-based resource allocation
        self.level_resources: Dict[str, int] = {
            "L0": 1,  # Molecular
            "L1": 1,  # Cellular
            "L2": 1,  # Tissue
            "L3": 1,  # Organ
            "L4": 1,  # Organism
            "L5": 1,  # Ecosystem
        }
        
        # Entropy monitoring
        self.level_entropy: Dict[str, deque] = {
            level: deque(maxlen=100) for level in self.level_resources.keys()
        }
        
        # Execution context
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        
        # Statistics
        self.stats = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "resource_reallocations": 0,
        }
    
    def schedule(self, task: ScheduledTask) -> None:
        """Schedule a task for execution."""
        if len(self.task_queue) >= self.max_queue_size:
            raise RuntimeError("Task queue is full")
        
        self.task_queue[task.id] = task
        self.stats["tasks_scheduled"] += 1
        
        logger.debug(f"Scheduled task {task.id} ({task.name}) at level {task.level}")
    
    def execute(self) -> None:
        """Execute scheduled tasks with adaptive resource allocation."""
        self.is_running = True
        
        try:
            while self.is_running and (self.task_queue or self.running_tasks):
                # Update resource allocation based on entropy
                self._update_resource_allocation()
                
                # Start new tasks based on available resources
                self._start_ready_tasks()
                
                # Check completed tasks
                self._check_completed_tasks()
                
                # Brief pause to prevent busy waiting
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        finally:
            self.is_running = False
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.is_running = False
        self.executor.shutdown(wait=True)
    
    def _update_resource_allocation(self) -> None:
        """Update resource allocation based on entropy anomalies."""
        # Compute entropy derivatives for each level
        entropy_derivatives = {}
        
        for level, entropy_history in self.level_entropy.items():
            if len(entropy_history) >= 2:
                # Simple derivative approximation
                recent_values = list(entropy_history)[-10:]  # Last 10 values
                if len(recent_values) >= 2:
                    derivative = np.mean(np.diff(recent_values))
                    entropy_derivatives[level] = abs(derivative)
                else:
                    entropy_derivatives[level] = 0.0
            else:
                entropy_derivatives[level] = 0.0
        
        # Reallocate resources to levels with high entropy changes
        if entropy_derivatives:
            max_derivative = max(entropy_derivatives.values())
            
            if max_derivative > self.entropy_threshold:
                # Find level with highest entropy change
                critical_level = max(entropy_derivatives, key=entropy_derivatives.get)
                
                # Increase resources for critical level
                old_resources = self.level_resources[critical_level]
                new_resources = min(
                    int(old_resources * self.zoom_factor),
                    self.max_workers
                )
                
                if new_resources > old_resources:
                    self.level_resources[critical_level] = new_resources
                    self.stats["resource_reallocations"] += 1
                    
                    logger.info(
                        f"Increased resources for level {critical_level}: "
                        f"{old_resources} -> {new_resources} "
                        f"(entropy derivative: {max_derivative:.6f})"
                    )
                    
                    # Decrease resources for other levels if needed
                    total_resources = sum(self.level_resources.values())
                    if total_resources > self.max_workers:
                        self._rebalance_resources()
    
    def _rebalance_resources(self) -> None:
        """Rebalance resources across levels to stay within limits."""
        total_resources = sum(self.level_resources.values())
        
        if total_resources <= self.max_workers:
            return
        
        # Reduce resources proportionally
        scale_factor = self.max_workers / total_resources
        
        for level in self.level_resources:
            old_value = self.level_resources[level]
            new_value = max(1, int(old_value * scale_factor))
            self.level_resources[level] = new_value
    
    def _start_ready_tasks(self) -> None:
        """Start tasks that are ready to execute."""
        # Count running tasks by level
        level_running_count = {}
        for task_id, future in self.running_tasks.items():
            if task_id in self.task_queue:
                level = self.task_queue[task_id].level
                level_running_count[level] = level_running_count.get(level, 0) + 1
        
        # Sort tasks by priority and creation time
        ready_tasks = []
        for task in self.task_queue.values():
            if self._is_task_ready(task) and task.id not in self.running_tasks:
                ready_tasks.append(task)
        
        ready_tasks.sort(key=lambda t: (-t.priority, t.created_at))
        
        # Start tasks based on available resources per level
        for task in ready_tasks:
            level_running = level_running_count.get(task.level, 0)
            level_capacity = self.level_resources.get(task.level, 1)
            
            if level_running < level_capacity:
                self._start_task(task)
                level_running_count[task.level] = level_running + 1
    
    def _is_task_ready(self, task: ScheduledTask) -> bool:
        """Check if a task is ready to execute (dependencies satisfied)."""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _start_task(self, task: ScheduledTask) -> None:
        """Start executing a task."""
        task.started_at = time.time()
        
        # Submit task to thread pool
        future = self.executor.submit(self._execute_task, task)
        self.running_tasks[task.id] = future
        
        logger.debug(f"Started task {task.id} ({task.name}) at level {task.level}")
    
    def _execute_task(self, task: ScheduledTask) -> Any:
        """Execute a single task."""
        try:
            # Call the task function
            result = task.function(*task.args, **task.kwargs)
            task.result = result
            task.completed_at = time.time()
            
            return result
            
        except Exception as e:
            task.error = e
            task.completed_at = time.time()
            logger.error(f"Task {task.id} failed: {e}")
            raise
    
    def _check_completed_tasks(self) -> None:
        """Check for completed tasks and handle results."""
        completed_task_ids = []
        
        for task_id, future in self.running_tasks.items():
            if future.done():
                completed_task_ids.append(task_id)
                task = self.task_queue[task_id]
                
                try:
                    # Get result (will raise exception if task failed)
                    future.result()
                    
                    # Task completed successfully
                    self.completed_tasks[task_id] = task
                    self.stats["tasks_completed"] += 1
                    
                    if task.started_at and task.completed_at:
                        execution_time = task.completed_at - task.started_at
                        self.stats["total_execution_time"] += execution_time
                    
                    logger.debug(f"Task {task_id} completed successfully")
                    
                except Exception as e:
                    # Task failed
                    task.error = e
                    task.retry_count += 1
                    
                    if task.retry_count <= task.max_retries:
                        # Retry the task
                        logger.warning(f"Retrying task {task_id} ({task.retry_count}/{task.max_retries})")
                        # Reset timing
                        task.started_at = None
                        task.completed_at = None
                        task.error = None
                    else:
                        # Task failed permanently
                        self.failed_tasks[task_id] = task
                        self.stats["tasks_failed"] += 1
                        logger.error(f"Task {task_id} failed permanently: {e}")
        
        # Clean up completed tasks
        for task_id in completed_task_ids:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            if task_id in self.task_queue:
                # Only remove if completed or permanently failed
                if (task_id in self.completed_tasks or 
                    task_id in self.failed_tasks):
                    del self.task_queue[task_id]
    
    def add_entropy_measurement(self, level: str, entropy: float) -> None:
        """Add entropy measurement for adaptive resource allocation."""
        if level in self.level_entropy:
            self.level_entropy[level].append(entropy)
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            "is_running": self.is_running,
            "queued_tasks": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "level_resources": self.level_resources.copy(),
            "statistics": self.stats.copy(),
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check all task collections
        for collection_name, collection in [
            ("queued", self.task_queue),
            ("completed", self.completed_tasks),
            ("failed", self.failed_tasks)
        ]:
            if task_id in collection:
                task = collection[task_id]
                status = {
                    "id": task.id,
                    "name": task.name,
                    "level": task.level,
                    "priority": task.priority,
                    "status": collection_name,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "retry_count": task.retry_count,
                }
                
                if task.error:
                    status["error"] = str(task.error)
                
                # Check if currently running
                if task_id in self.running_tasks:
                    status["status"] = "running"
                
                return status
        
        return None
    
    def clear_completed_tasks(self) -> None:
        """Clear completed and failed tasks to free memory."""
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        logger.info("Cleared completed and failed tasks")
    
    def summary(self) -> str:
        """Get summary of scheduler state."""
        status = self.get_status()
        
        lines = [
            "Adaptive Scheduler Status:",
            f"  Running: {status['is_running']}",
            f"  Queued: {status['queued_tasks']}",
            f"  Running: {status['running_tasks']}",
            f"  Completed: {status['completed_tasks']}",
            f"  Failed: {status['failed_tasks']}",
            "",
            "Resource Allocation:",
        ]
        
        for level, resources in status['level_resources'].items():
            lines.append(f"  {level}: {resources} workers")
        
        stats = status['statistics']
        lines.extend([
            "",
            "Statistics:",
            f"  Total scheduled: {stats['tasks_scheduled']}",
            f"  Success rate: {stats['tasks_completed']/max(1, stats['tasks_scheduled'])*100:.1f}%",
            f"  Avg execution time: {stats['total_execution_time']/max(1, stats['tasks_completed']):.3f}s",
            f"  Resource reallocations: {stats['resource_reallocations']}",
        ])
        
        return "\n".join(lines)
