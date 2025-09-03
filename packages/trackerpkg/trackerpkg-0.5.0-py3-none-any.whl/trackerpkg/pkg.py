import json
import os
import time
import functools
import aiohttp
import psutil
import threading
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from confluent_kafka import Producer
import inspect
from urllib.parse import urlparse
import requests
import http.client
import urllib.request
from collections import Counter
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXCLUDED_DOMAINS = {"api.openai.com"}

@dataclass
class SDKConfig:
    """Centralized configuration for the SDK"""
    api_base_url: str = "http://34.34.101.236:8000"
    api_timeout: int = 30
    kafka_config_path: str = "client.properties"
    sampling_interval: float = 0.1
    max_samples: int = 1000
    kafka_flush_timeout: float = 5.0
    enable_detailed_metrics: bool = True
    message_ttl_seconds: int = 3600
    max_error_retries: int = 3
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables with validation"""
        load_dotenv()
        
        # Validate critical environment variables
        required_vars = ['KAFKA_BOOTSTRAP_SERVERS']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return cls(
            api_base_url=os.environ.get('DYNAMETER_API_BASE_URL', cls.api_base_url),
            api_timeout=int(os.environ.get('DYNAMETER_API_TIMEOUT', str(cls.api_timeout))),
            sampling_interval=float(os.environ.get('DYNAMETER_SAMPLING_INTERVAL', str(cls.sampling_interval))),
            max_samples=int(os.environ.get('DYNAMETER_MAX_SAMPLES', str(cls.max_samples))),
            kafka_flush_timeout=float(os.environ.get('DYNAMETER_KAFKA_TIMEOUT', str(cls.kafka_flush_timeout))),
        )

# Global config instance
config = SDKConfig.from_env()

def safe_json_dumps(obj):
    """Safely serialize objects to JSON with fallback handling"""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        logger.warning(f"Initial JSON serialization failed: {e}")
        try:
            # Try with default=str fallback
            return json.dumps(obj, default=str)
        except Exception as e2:
            error_msg = f"Complete JSON serialization failure: {e2}"
            logger.error(error_msg)
            report_sdk_error(error_msg, {"object_type": type(obj).__name__})
            return json.dumps({"error": "serialization_failed", "timestamp": time.time()})

def safe_get_process():
    """Safely get current process with error handling"""
    try:
        return psutil.Process(os.getpid())
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as e:
        logger.error(f"Failed to access process info: {e}")
        report_sdk_error(f"Process access failed: {e}")
        return None

class MessageTracker:
    """Ensures each request_id + function_name combination sends only one message"""
    
    def __init__(self):
        self._sent_messages = {}
        self._lock = threading.RLock()
    
    def should_send(self, request_id: str, function_name: str, message_type: str) -> bool:
        """Check if this message should be sent (prevents duplicates)"""
        key = f"{request_id}:{function_name}:{message_type}"
        current_time = time.time()
        
        with self._lock:
            # Cleanup old entries
            self._cleanup_old_entries(current_time)
            
            if key in self._sent_messages:
                return False
            self._sent_messages[key] = current_time
            return True
    
    def _cleanup_old_entries(self, current_time: float):
        """Cleanup old entries to prevent memory leaks - THREAD SAFE"""
        cutoff_time = current_time - config.message_ttl_seconds
        # Create list first to avoid modifying dict during iteration
        keys_to_remove = [
            key for key, timestamp in list(self._sent_messages.items()) 
            if timestamp < cutoff_time
        ]
        for key in keys_to_remove:
            self._sent_messages.pop(key, None)  # Use pop with default to avoid KeyError

# Global tracker instance
message_tracker = MessageTracker()

class KafkaProducerPool:
    """Thread-safe Kafka producer pool to avoid creating multiple producers"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._producer = None
                    cls._instance._producer_lock = threading.Lock()
        return cls._instance
    
    def get_producer(self):
        if self._producer is None:
            with self._producer_lock:
                if self._producer is None:
                    try:
                        cfg = read_kafka_config_env()
                        self._producer = Producer(cfg)
                    except Exception as e:
                        logger.error(f"Failed to create Kafka producer: {e}")
                        report_sdk_error(f"Kafka producer creation failed: {e}")
                        raise
        return self._producer

def report_sdk_error(error_message: str, context: Dict[str, Any] = None, max_retries: int = None):
    """
    Report an SDK error to GCP Cloud Run function with retry logic.
    """
    if max_retries is None:
        max_retries = config.max_error_retries
        
    try:
        cloud_run_url = "https://dynameter-sdk-error-logging-852559162595.europe-west1.run.app"
        if not cloud_run_url:
            logger.warning("No ERROR_HANDLER_URL configured")
            return False

        data = {
            "error_message": error_message,
            "context": context or {},
            "timestamp": time.time(),
            "message_id": str(uuid.uuid4()),
        }

        # Send with retry logic
        for attempt in range(max_retries):
            try:
                headers = {"Content-Type": "application/json"}
                timeout = min(10 + (attempt * 5), 30)  # Progressive timeout
                response = requests.post(
                    cloud_run_url, 
                    json=data, 
                    headers=headers, 
                    timeout=timeout
                )
                response.raise_for_status()
                return True
            except (requests.RequestException, requests.Timeout) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to report error after {max_retries} attempts: {e}")
                    return False
                time.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                
    except Exception as e:
        logger.error(f"Unexpected error while reporting SDK error: {e}")
        return False

def get_api_config():
    """Get FastAPI configuration from environment variables."""
    return {
        'base_url': config.api_base_url,
        'timeout': config.api_timeout
    }

def read_kafka_config():
    """Read Kafka configuration from client.properties file."""
    kafka_config = {}
    try:
        with open(config.kafka_config_path) as fh:
            for line in fh:
                line = line.strip()
                if len(line) != 0 and line[0] != "#":
                    parameter, value = line.strip().split('=', 1)
                    kafka_config[parameter] = value.strip()
    except FileNotFoundError:
        logger.error(f"Kafka config file not found: {config.kafka_config_path}")
        raise
    return kafka_config

def read_kafka_config_env():
    """Read Kafka configuration from environment variables."""
    kafka_config = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
        'security.protocol': os.environ.get('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL'),
        'sasl.mechanisms': os.environ.get('KAFKA_SASL_MECHANISMS', 'PLAIN'),
        'sasl.username': os.environ.get('KAFKA_SASL_USERNAME'),
        'sasl.password': os.environ.get('KAFKA_SASL_PASSWORD'),
        'session.timeout.ms': os.environ.get('KAFKA_SESSION_TIMEOUT', '45000'),
        'client.id': os.environ.get('KAFKA_CLIENT_ID', 'python-client')
    }
    
    # Remove None values
    kafka_config = {k: v for k, v in kafka_config.items() if v is not None}
    
    if not kafka_config.get('bootstrap.servers'):
        raise ValueError("KAFKA_BOOTSTRAP_SERVERS environment variable is required")
    
    return kafka_config

def get_kafka_producer():
    """Get singleton Kafka producer instance."""
    return KafkaProducerPool().get_producer()

def safe_send_to_kafka(topic: str, key: str, value: str, max_retries: int = 3) -> bool:
    """Send to Kafka with retry logic and better error handling"""
    try:
        producer = get_kafka_producer()
    except Exception as e:
        logger.error(f"Failed to get Kafka producer: {e}")
        return False
    
    for attempt in range(max_retries):
        try:
            producer.produce(topic, key=key, value=value)
            producer.flush(timeout=config.kafka_flush_timeout)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                error_msg = f"Failed to send to Kafka after {max_retries} attempts: {e}"
                logger.error(error_msg)
                report_sdk_error(error_msg, {
                    "topic": topic,
                    "key": key,
                    "attempt": attempt + 1
                })
                return False
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    return False

def send_to_api_sync(endpoint: str, data: Dict[str, Any], timeout: int = None) -> bool:
    """Send data to FastAPI endpoint synchronously with retry logic."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            api_config = get_api_config()
            url = f"{api_config['base_url']}{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            # Add message metadata
            data['message_id'] = str(uuid.uuid4())
            data['created_at'] = datetime.utcnow().isoformat()
            data['version'] = '1.0'
            
            request_timeout = timeout or api_config['timeout']
            if attempt > 0:
                request_timeout += attempt * 10  # Progressive timeout
            
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=request_timeout
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            if attempt == max_retries - 1:
                error_msg = f"Error sending data to API endpoint {endpoint} after {max_retries} attempts: {e}"
                logger.error(error_msg)
                report_sdk_error(error_msg, {"endpoint": endpoint, "data": str(data)[:500]})
                return False
            time.sleep(0.5 * (2 ** attempt))
    return False

def openai_token_usage(response):
    """
    Unified extractor for OpenAI responses with error handling
    """
    try:
        model = None
        prompt = None
        completion = None
        total = None

        if hasattr(response, "model") and hasattr(response, "usage"):
            model = getattr(response, "model", None)
            usage = getattr(response, "usage", None)
            if usage:
                prompt = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None)
                completion = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)
                total = getattr(usage, "total_tokens", None)
            return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

        if isinstance(response, dict):
            model = response.get("model")
            usage = response.get("usage", {}) or {}
            prompt = usage.get("prompt_tokens") or usage.get("input_tokens")
            completion = usage.get("completion_tokens") or usage.get("output_tokens")
            total = usage.get("total_tokens")
            return {"model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}

        raise ValueError("Unsupported response object: model or usage not found")
    
    except Exception as e:
        logger.error(f"Failed to extract token usage: {e}")
        report_sdk_error(f"Token usage extraction failed: {e}")
        return {"model": "unknown", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

class RollingMetrics:
    """Rolling window for metrics to prevent unlimited memory growth"""
    
    def __init__(self, max_size: int = None):
        self.max_size = max_size or config.max_samples
        self.data = []
        self.lock = threading.Lock()
    
    def add_sample(self, sample):
        with self.lock:
            self.data.append(sample)
            if len(self.data) > self.max_size:
                # Keep only the most recent 25% to prevent frequent resizing
                keep_size = max(self.max_size // 4, 10)
                self.data = self.data[-keep_size:]
    
    def get_stats(self):
        with self.lock:
            if not self.data:
                return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
            return {
                'count': len(self.data),
                'avg': sum(self.data) / len(self.data),
                'min': min(self.data),
                'max': max(self.data)
            }
    
    def get_data_copy(self):
        with self.lock:
            return self.data.copy()

class AtomicResourceTracker:
    """Ensures resource metrics are captured atomically without race conditions"""
    
    def __init__(self, request_id: str, customer_id: str, function_name: str, send_to_kafka: bool = True):
        self.request_id = request_id
        self.customer_id = customer_id
        self.function_name = function_name
        self.send_to_kafka = send_to_kafka
        self._metrics_captured = False
        self._lock = threading.Lock()
        self._process = safe_get_process()  # Use safe process getter
        self._execution_id = f"{request_id}_{threading.get_ident()}_{int(time.time()*1000000)}"
        
    def __enter__(self):
        with self._lock:
            if self._metrics_captured:
                raise RuntimeError("Resource tracking already in progress for this instance")
            
            if self._process is None:
                logger.warning(f"Process monitoring unavailable for {self.function_name}")
                return self
            
            try:
                self._start_time = time.time()
                self._cpu_times_start = self._process.cpu_times()
                
                # Initialize system metrics
                self._mem_info_before = psutil.virtual_memory()
                self._logical_cores = psutil.cpu_count(logical=True)
                self._physical_cores = psutil.cpu_count(logical=False)
                
                # Start controlled sampling
                self._stop_event = threading.Event()
                self._mem_samples = RollingMetrics()
                self._cpu_samples = []
                self._thread_samples = []
                self._sampling_thread = threading.Thread(target=self._sample_metrics, daemon=True)
                self._sampling_thread.start()
                
            except Exception as e:
                logger.error(f"Failed to initialize resource tracking: {e}")
                report_sdk_error(f"Resource tracking initialization failed: {e}")
                
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            if self._metrics_captured or self._process is None:
                return  # Already processed or process unavailable
                
            try:
                self._end_time = time.time()
                self._cpu_times_end = self._process.cpu_times()
                
                # Stop sampling with proper cleanup
                self._stop_event.set()
                if hasattr(self, '_sampling_thread') and self._sampling_thread.is_alive():
                    self._sampling_thread.join(timeout=2)  # Increased timeout
                    if self._sampling_thread.is_alive():
                        error_msg = f"Sampling thread failed to terminate for {self.function_name}"
                        logger.warning(error_msg)
                        report_sdk_error(error_msg, {"execution_id": self._execution_id})
                
                # Calculate final metrics
                self._calculate_final_metrics()
                self._metrics_captured = True
                
                # Send to destinations only once
                if message_tracker.should_send(self.request_id, self.function_name, "resource"):
                    self._send_metrics()
                else:
                    logger.debug(f"Duplicate resource message blocked for {self.function_name}")
                    
            except Exception as e:
                logger.error(f"Error in resource tracker cleanup: {e}")
                report_sdk_error(f"Resource tracker cleanup failed: {e}")
    
    def _sample_metrics(self):
        """Sample memory usage in controlled intervals"""
        while not self._stop_event.is_set():
            try:
                if self._process is None:
                    break
                    
                mem_gb = self._process.memory_info().rss / (1024 ** 3)
                self._mem_samples.add_sample(mem_gb)
                
                # Collect additional CPU metrics
                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": self._process.cpu_percent(),
                    "num_threads": self._process.num_threads(),
                    "memory_rss": self._process.memory_info().rss
                }
                self._cpu_samples.append(sample)
                self._thread_samples.append(threading.active_count())
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.warning("Process access lost during sampling")
                break
            except Exception as e:
                logger.error(f"Error in metrics sampling: {e}")
                break
            
            # Wait with early termination check
            if self._stop_event.wait(config.sampling_interval):
                break
    
    def _calculate_final_metrics(self):
        """Calculate final metrics from collected samples"""
        try:
            duration = self._end_time - self._start_time
            
            # Validate duration
            if duration < 0:
                logger.warning(f"Negative duration detected: {duration}")
                duration = 0
            
            # CPU calculations - do it once, correctly
            user_cpu_time = self._cpu_times_end.user - self._cpu_times_start.user
            system_cpu_time = self._cpu_times_end.system - self._cpu_times_start.system
            total_cpu_time = user_cpu_time + system_cpu_time
            
            # Use the same value for cpu_seconds to ensure consistency
            cpu_seconds = total_cpu_time
            
            # CPU utilization and efficiency calculations
            cpu_utilization_percent = (total_cpu_time / duration * 100) if duration > 0 else 0
            cpu_efficiency = (total_cpu_time / (duration * self._logical_cores)) * 100 if duration > 0 and self._logical_cores > 0 else 0
            
            # Memory calculations
            mem_stats = self._mem_samples.get_stats()
            avg_memory_gb = mem_stats['avg']
            gb_seconds = avg_memory_gb * duration
            
            # System info
            try:
                mem_info_after = psutil.virtual_memory()
                system_cpu_usage = psutil.cpu_percent(interval=None)
            except Exception as e:
                logger.warning(f"Failed to get system metrics: {e}")
                mem_info_after = self._mem_info_before
                system_cpu_usage = 0.0
            
            # Validate CPU calculation consistency
            if abs(cpu_seconds - total_cpu_time) > 0.0001:  # Allow for small floating point differences
                error_msg = f"CPU calculation mismatch: cpu_seconds={cpu_seconds}, total_cpu_time={total_cpu_time}"
                logger.warning(error_msg)
                report_sdk_error(error_msg, {
                    "function": self.function_name,
                    "execution_id": self._execution_id,
                    "user_time": user_cpu_time,
                    "system_time": system_cpu_time
                })
            
            # Detailed system usage report
            detailed_metrics = {
                "time_taken_sec": round(duration, 4),
                "logical_cores": self._logical_cores,
                "physical_cores": self._physical_cores,
                "memory_usage_before_percent": round(self._mem_info_before.percent, 2),
                "memory_usage_after_percent": round(mem_info_after.percent, 2),
                "memory_available_gb": round(mem_info_after.available / (1024**3), 2),
                "memory_available_mb": round(mem_info_after.available / (1024**2), 2),
                "memory_used_gb": round(mem_info_after.used / (1024**3), 2),
                "memory_used_mb": round(mem_info_after.used / (1024**2), 2),
                "memory_total_gb": round(mem_info_after.total / (1024**3), 2),
                "memory_total_mb": round(mem_info_after.total / (1024**2), 2),
                "process_memory_gb": round(avg_memory_gb, 4),
                "process_memory_mb": round(avg_memory_gb * 1024, 2),
                "process_memory_rss_gb": round(self._process.memory_info().rss / (1024**3), 4),
                "process_memory_rss_mb": round(self._process.memory_info().rss / (1024**2), 2),
                "process_cpu_seconds_total": round(total_cpu_time, 4),
                "process_cpu_seconds_user": round(user_cpu_time, 4),
                "process_cpu_seconds_system": round(system_cpu_time, 4),
                "process_cpu_utilization_percent": round(cpu_utilization_percent, 2),
                "cpu_efficiency_percent": round(cpu_efficiency, 2),
                "container_isolated": system_cpu_usage == 0.0,
                "measurement_notes": "System CPU/memory metrics may be limited due to Cloud Run container isolation"
            }
            
            # Create final metrics object - ensure cpu_seconds matches detailed metrics
            self._final_metrics = {
                'request_id': self.request_id,
                'customer_id': self.customer_id,
                'function_name': self.function_name,
                'duration_sec': round(duration, 4),
                'cpu_seconds': round(cpu_seconds, 4),  # Rounded to match detailed metrics
                'gb_seconds': round(gb_seconds, 4),
                'detailed_cpu_metrics': detailed_metrics if self.send_to_kafka else json.dumps(detailed_metrics),
                'timestamp': self._end_time,
                'execution_id': self._execution_id
            }
            
        except Exception as e:
            logger.error(f"Error calculating final metrics: {e}")
            report_sdk_error(f"Metrics calculation failed: {e}")
            # Create minimal metrics object
            self._final_metrics = {
                'request_id': self.request_id,
                'customer_id': self.customer_id,
                'function_name': self.function_name,
                'duration_sec': 0,
                'cpu_seconds': 0,
                'gb_seconds': 0,
                'error': 'metrics_calculation_failed',
                'timestamp': time.time(),
                'execution_id': self._execution_id
            }
    
    def _send_metrics(self):
        """Send metrics to configured destinations"""
        try:
            if self.send_to_kafka:
                success = safe_send_to_kafka("CPU_MEMORY", self.function_name, safe_json_dumps(self._final_metrics))
                if not success:
                    logger.error(f"Failed to send resource metrics to Kafka for {self.function_name}")
            else:
                success = send_to_api_sync('/resource-metrics', self._final_metrics)
                if not success:
                    logger.error(f"Failed to send resource metrics to API for {self.function_name}")
        except Exception as e:
            error_msg = f"Error sending resource metrics: {e}"
            logger.error(error_msg)
            report_sdk_error(error_msg, {"function": self.function_name, "execution_id": self._execution_id})

class SequentialTokenTracker:
    """Processes token usage sequentially to avoid race conditions"""
    
    def __init__(self, request_id: str, customer_id: str, function_name: str, send_to_kafka: bool = True, topic: str = "OPENAI"):
        self.customer_id = customer_id
        self.request_id = request_id
        self.function_name = function_name
        self.topic = topic
        self.send_to_kafka = send_to_kafka
        self.responses = []
        self.original_methods = {}
        self.call_stack = []
        self.call_timestamps = []
        self._processing_lock = threading.Lock()
        self._start_time = None
        self._process = safe_get_process()
        self._execution_id = f"{request_id}_{threading.get_ident()}_{int(time.time()*1000000)}"
        self.openai_available = False
    
    def _is_openai_request(self, url: str, headers: dict = None) -> bool:
        """Check if this is an OpenAI API request"""
        try:
            if 'api.openai.com' in str(url).lower():
                return True
            # Also check for Authorization header with Bearer token (OpenAI pattern)
            if headers and isinstance(headers, dict):
                auth_header = headers.get('Authorization', '') or headers.get('authorization', '')
                return 'bearer ' in str(auth_header).lower()
            return False
        except:
            return False

    def _extract_openai_usage_from_response(self, response_data: dict, duration: float) -> dict:
        """Extract OpenAI token usage from response JSON"""
        try:
            if isinstance(response_data, dict):
                usage = response_data.get('usage', {})
                model = response_data.get('model', 'unknown')
                
                if usage and usage.get('total_tokens', 0) > 0:
                    return {
                        'model': model,
                        'prompt_tokens': usage.get('prompt_tokens', 0),
                        'completion_tokens': usage.get('completion_tokens', 0),
                        'total_tokens': usage.get('total_tokens', 0),
                        'call_duration': duration,
                        # Also include the additional details if present
                        'prompt_tokens_details': usage.get('prompt_tokens_details', {}),
                        'completion_tokens_details': usage.get('completion_tokens_details', {}),
                        'service_tier': response_data.get('service_tier', ''),
                        'system_fingerprint': response_data.get('system_fingerprint', '')
                    }
            return None
        except Exception as e:
            logger.debug(f"Failed to extract OpenAI usage: {e}")
            return None

    def _patch_requests_for_openai(self):
        """Patch requests specifically to catch OpenAI API calls"""
        try:
            import requests
            
            # Store original method
            self.original_requests_post = requests.post
            self.original_requests_request = requests.request
            
            tracker = self
            
            def requests_post_wrapper(*args, **kwargs):
                # Get URL and headers
                url = args[0] if args else kwargs.get('url', '')
                headers = kwargs.get('headers', {})
                
                if tracker._is_openai_request(url, headers):
                    call_start = time.time()
                    calling_frame = inspect.currentframe().f_back
                    calling_function = calling_frame.f_code.co_name
                    
                    try:
                        response = tracker.original_requests_post(*args, **kwargs)
                        call_end = time.time()
                        
                        # Try to extract JSON and process OpenAI response
                        if response.status_code == 200:
                            try:
                                response_data = response.json()
                                usage = tracker._extract_openai_usage_from_response(
                                    response_data, call_end - call_start
                                )
                                
                                if usage:
                                    with tracker._processing_lock:
                                        # Create a mock response object that matches OpenAI library format
                                        mock_response = type('MockResponse', (), {
                                            'usage': type('Usage', (), usage)(),
                                            'model': usage['model']
                                        })()
                                        
                                        tracker.responses.append(mock_response)
                                        tracker.call_stack.append(calling_function)
                                        tracker.call_timestamps.append({
                                            'start': call_start,
                                            'end': call_end,
                                            'duration': call_end - call_start
                                        })
                            except:
                                pass  # Not JSON or not OpenAI format
                        
                        return response
                    except Exception as e:
                        call_end = time.time()
                        # Still record the call even if it failed
                        raise e
                else:
                    return tracker.original_requests_post(*args, **kwargs)
            
            def requests_request_wrapper(*args, **kwargs):
                # Handle general requests.request() calls
                method = args[0] if args else kwargs.get('method', 'GET')
                url = args[1] if len(args) > 1 else kwargs.get('url', '')
                headers = kwargs.get('headers', {})
                
                if method.upper() == 'POST' and tracker._is_openai_request(url, headers):
                    call_start = time.time()
                    calling_frame = inspect.currentframe().f_back
                    calling_function = calling_frame.f_code.co_name
                    
                    try:
                        response = tracker.original_requests_request(*args, **kwargs)
                        call_end = time.time()
                        
                        if response.status_code == 200:
                            try:
                                response_data = response.json()
                                usage = tracker._extract_openai_usage_from_response(
                                    response_data, call_end - call_start
                                )
                                
                                if usage:
                                    with tracker._processing_lock:
                                        mock_response = type('MockResponse', (), {
                                            'usage': type('Usage', (), usage)(),
                                            'model': usage['model']
                                        })()
                                        
                                        tracker.responses.append(mock_response)
                                        tracker.call_stack.append(calling_function)
                                        tracker.call_timestamps.append({
                                            'start': call_start,
                                            'end': call_end,
                                            'duration': call_end - call_start
                                        })
                            except:
                                pass
                        
                        return response
                    except Exception as e:
                        raise e
                else:
                    return tracker.original_requests_request(*args, **kwargs)
            
            # Apply patches
            requests.post = requests_post_wrapper
            requests.request = requests_request_wrapper
            
        except Exception as e:
            logger.error(f"Failed to patch requests for OpenAI tracking: {e}")
    
    def __enter__(self):
        self._start_time = time.time()
        
        # First try to patch OpenAI library
        try:
            from openai import OpenAI
            from openai.resources.chat import completions
            from openai.resources import embeddings
            
            self.openai_available = True
            
            # Store original methods
            self.original_chat_create = completions.Completions.create
            self.original_embeddings_create = embeddings.Embeddings.create
            
            # Create wrapper functions that track the calling function
            def chat_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_chat_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                with self._processing_lock:
                    self.responses.append(response)
                    self.call_stack.append(calling_function)
                    self.call_timestamps.append({
                        'start': call_start,
                        'end': call_end,
                        'duration': call_end - call_start
                    })
                    
                return response
            
            def embeddings_wrapper(self_inner, *args, **kwargs):
                call_start = time.time()
                calling_frame = inspect.currentframe().f_back
                calling_function = calling_frame.f_code.co_name
                
                response = self.original_embeddings_create(self_inner, *args, **kwargs)
                call_end = time.time()
                
                with self._processing_lock:
                    self.responses.append(response)
                    self.call_stack.append(calling_function)
                    self.call_timestamps.append({
                        'start': call_start,
                        'end': call_end,
                        'duration': call_end - call_start
                    })
                    
                return response
            
            # Monkey patch the methods
            completions.Completions.create = chat_wrapper
            embeddings.Embeddings.create = embeddings_wrapper
            
        except ImportError as e:
            error_msg = f"OpenAI library not available for token tracking: {e}"
            logger.warning(error_msg)
            report_sdk_error(error_msg, {"function": self.function_name})
            self.openai_available = False
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI tracking: {e}"
            logger.error(error_msg)
            report_sdk_error(error_msg, {"function": self.function_name})
            self.openai_available = False
        
        # Also patch requests for direct OpenAI API calls
        self._patch_requests_for_openai()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Always restore original methods in finally block
        try:
            # Process all responses sequentially
            with self._processing_lock:
                self._process_all_responses()
        finally:
            # Restore OpenAI library methods
            if self.openai_available:
                try:
                    from openai.resources.chat import completions
                    from openai.resources import embeddings
                    
                    completions.Completions.create = self.original_chat_create
                    embeddings.Embeddings.create = self.original_embeddings_create
                except Exception as e:
                    logger.error(f"Failed to restore OpenAI methods: {e}")
            
            # Restore requests methods
            try:
                if hasattr(self, 'original_requests_post'):
                    import requests
                    requests.post = self.original_requests_post
                if hasattr(self, 'original_requests_request'):
                    import requests
                    requests.request = self.original_requests_request
            except Exception as e:
                logger.error(f"Failed to restore requests methods: {e}")
    
    def _process_all_responses(self):
        """Process all collected responses in sequence"""
        for i, (response, calling_function, timing) in enumerate(zip(
            self.responses, self.call_stack, self.call_timestamps
        )):
            try:
                usage = openai_token_usage(response)
                if usage and usage.get('total_tokens', 0) > 0:
                    # Create unique function name for this call
                    if calling_function == self.function_name:
                        function_name = f"{self.function_name}_call_{i+1}" if len(self.responses) > 1 else self.function_name
                    else:
                        function_name = f"{self.function_name}_{calling_function}_call_{i+1}"
                    
                    usage['call_duration'] = timing['duration']
                    
                    # Check for duplicates before sending
                    if message_tracker.should_send(self.request_id, function_name, "token"):
                        self._send_token_usage(function_name, usage)
                    else:
                        logger.debug(f"Duplicate token message blocked for {function_name}")
                        
            except Exception as e:
                error_msg = f"Error processing token usage for call {i+1}: {e}"
                logger.error(error_msg)
                report_sdk_error(error_msg, {"function": self.function_name, "execution_id": self._execution_id})
    
    def _send_token_usage(self, function_name: str, usage: Dict[str, Any]):
        """Send token usage metrics"""
        message = {
            'customer_id': self.customer_id,
            'request_id': self.request_id,
            'function_name': function_name,
            'model': usage['model'],
            'prompt_tokens': usage['prompt_tokens'],
            'completion_tokens': usage['completion_tokens'],
            'total_tokens': usage['total_tokens'],
            'call_duration': usage['call_duration'],
            'timestamp': time.time(),
            'execution_id': self._execution_id
        }
        
        try:
            if self.send_to_kafka:
                success = safe_send_to_kafka(self.topic, function_name, safe_json_dumps(message))
                if not success:
                    logger.error(f"Failed to send token usage to Kafka for {function_name}")
            else:
                success = send_to_api_sync('/token-usage', message)
                if not success:
                    logger.error(f"Failed to send token usage to API for {function_name}")
        except Exception as e:
            error_msg = f"Error sending token usage: {e}"
            logger.error(error_msg)
            report_sdk_error(error_msg, {"function": function_name, "execution_id": self._execution_id})
            
class ThirdPartyAPITracker:
    """Context manager that tracks third-party API calls."""

    def __init__(self, request_id: str, customer_id: str, function_name: str, 
                 send_to_kafka: bool = True, kafka_topic: str = 'TP_APIS'):
        self.request_id = request_id
        self.customer_id = customer_id
        self.function_name = function_name
        self.kafka_topic = kafka_topic if send_to_kafka else None
        self.send_to_kafka = send_to_kafka
        self.api_counter = Counter()
        self.api_timings = {}
        self._counter_lock = threading.Lock()
        self.original_methods = {}
        self._process = safe_get_process()
        self._start_time = time.time()
        self._execution_id = f"{request_id}_{threading.get_ident()}_{int(time.time()*1000000)}"

    def _should_track(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc
            return domain and domain.lower() not in EXCLUDED_DOMAINS
        except Exception:
            return False

    def _record_api_call(self, domain: str, duration: float = 0.1):
        """Record an API call with timing information."""
        with self._counter_lock:
            self.api_counter[domain] += 1
            if domain not in self.api_timings:
                self.api_timings[domain] = []
            self.api_timings[domain].append(duration)

    def _patch_requests(self):
        original = requests.Session.request
        self.original_methods["requests"] = original
        tracker = self

        def wrapped(session, method, url, *args, **kwargs):
            if tracker._should_track(url):
                domain = urlparse(url).netloc
                start_time = time.time()
                try:
                    response = original(session, method, url, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return original(session, method, url, *args, **kwargs)

        requests.Session.request = wrapped

    def _patch_http_client(self):
        original = http.client.HTTPConnection.request
        self.original_methods["http_client"] = original
        tracker = self

        def wrapped(conn, method, url, *args, **kwargs):
            host = getattr(conn, "host", None)
            scheme = getattr(conn, "scheme", "http")
            if host:
                full_url = f"{scheme}://{host}{url}"
                if tracker._should_track(full_url):
                    start_time = time.time()
                    try:
                        response = original(conn, method, url, *args, **kwargs)
                        duration = time.time() - start_time
                        tracker._record_api_call(host, duration)
                        return response
                    except Exception as e:
                        duration = time.time() - start_time
                        tracker._record_api_call(host, duration)
                        raise e
            return original(conn, method, url, *args, **kwargs)

        http.client.HTTPConnection.request = wrapped

    def _patch_urllib(self):
        original = urllib.request.OpenerDirector.open
        self.original_methods["urllib"] = original
        tracker = self

        def wrapped(opener, fullurl, *args, **kwargs):
            url_str = fullurl.get_full_url() if hasattr(fullurl, "get_full_url") else str(fullurl)
            if tracker._should_track(url_str):
                domain = urlparse(url_str).netloc
                start_time = time.time()
                try:
                    response = original(opener, fullurl, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return original(opener, fullurl, *args, **kwargs)

        urllib.request.OpenerDirector.open = wrapped

    def _patch_aiohttp(self):
        if aiohttp is None:
            return

        original = aiohttp.ClientSession._request
        self.original_methods["aiohttp"] = original
        tracker = self

        async def wrapped(session, method, url, *args, **kwargs):
            if tracker._should_track(url):
                domain = urlparse(url).netloc
                start_time = time.time()
                try:
                    response = await original(session, method, url, *args, **kwargs)
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    tracker._record_api_call(domain, duration)
                    raise e
            else:
                return await original(session, method, url, *args, **kwargs)

        aiohttp.ClientSession._request = wrapped

    def __enter__(self):
        try:
            self._patch_requests()
            self._patch_http_client()
            self._patch_urllib()
            self._patch_aiohttp()
        except Exception as e:
            logger.error(f"Failed to patch HTTP libraries: {e}")
            report_sdk_error(f"HTTP patching failed: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Always restore originals in finally block
        try:
            # Send metrics only once
            if message_tracker.should_send(self.request_id, self.function_name, "api"):
                if self.send_to_kafka:
                    self._send_to_kafka()
                else:
                    self._log_to_api()
            else:
                logger.debug(f"Duplicate API message blocked for {self.function_name}")
        finally:
            # Restore original methods
            for key, method in self.original_methods.items():
                try:
                    if key == "requests":
                        requests.Session.request = method
                    elif key == "http_client":
                        http.client.HTTPConnection.request = method
                    elif key == "urllib":
                        urllib.request.OpenerDirector.open = method
                    elif key == "aiohttp" and aiohttp:
                        aiohttp.ClientSession._request = method
                except Exception as e:
                    logger.error(f"Failed to restore {key} method: {e}")

    def _send_to_kafka(self):
        """Send API usage metrics to Kafka"""
        # Create thread-safe snapshots to avoid "dictionary changed size during iteration"
        with self._counter_lock:
            api_counter_snapshot = dict(self.api_counter)
            api_timings_snapshot = {k: list(v) for k, v in self.api_timings.items()}
        
        message = {
            "customer_id": self.customer_id,
            "request_id": self.request_id,
            "function_name": self.function_name,
            "api_calls": api_counter_snapshot,
            "api_timings": {domain: {
                "avg_duration": sum(timings) / len(timings) if timings else 0,
                "total_calls": len(timings)
            } for domain, timings in api_timings_snapshot.items()},
            "timestamp": time.time(),
            "execution_id": self._execution_id
        }
        try:
            success = safe_send_to_kafka(self.kafka_topic, self.function_name, safe_json_dumps(message))
            if not success:
                logger.error(f"Failed to send API usage to Kafka for {self.function_name}")
        except Exception as e:
            error_msg = f"Error sending API tracker metrics to Kafka: {e}"
            logger.error(error_msg)
            report_sdk_error(error_msg, {"function": self.function_name, "execution_id": self._execution_id})

    def _log_to_api(self):
        """Send third-party API usage to FastAPI endpoint"""
        # Create thread-safe snapshots to avoid "dictionary changed size during iteration"
        with self._counter_lock:
            api_counter_snapshot = dict(self.api_counter)
            api_timings_snapshot = {k: list(v) for k, v in self.api_timings.items()}
        
        for domain, count in api_counter_snapshot.items():
            avg_duration = 0
            if domain in api_timings_snapshot and api_timings_snapshot[domain]:
                avg_duration = sum(api_timings_snapshot[domain]) / len(api_timings_snapshot[domain])
            
            data = {
                'request_id': self.request_id,
                'customer_id': self.customer_id,
                'function_name': self.function_name,
                'api_domain': domain,
                'call_count': count,
                'avg_duration': avg_duration,
                'execution_id': self._execution_id
            }
            
            success = send_to_api_sync('/api-usage', data)
            if not success:
                logger.error(f"Failed to send API usage to DB for {self.function_name}, domain: {domain}")

class KafkaMessageDeduplicator:
    """Deduplicate messages at the consumer level as a safety net"""
    
    def __init__(self, ttl_seconds: int = None):
        self._processed_messages = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds or config.message_ttl_seconds
    
    def is_duplicate(self, message_data: dict) -> bool:
        """Check if this message has been processed recently"""
        key = self._create_message_key(message_data)
        current_time = time.time()
        
        with self._lock:
            self._cleanup_old_entries(current_time)
            
            if key in self._processed_messages:
                return True
                
            self._processed_messages[key] = current_time
            return False
    
    def _create_message_key(self, message_data: dict) -> str:
        """Create a unique key from message content"""
        try:
            # For resource messages
            if 'duration_sec' in message_data:
                return f"resource:{message_data.get('customer_id')}:{message_data.get('request_id')}:{message_data.get('function_name')}"
            
            # For token messages  
            elif 'model' in message_data:
                return f"token:{message_data.get('customer_id')}:{message_data.get('request_id')}:{message_data.get('function_name')}"
                
            # For API messages
            elif 'api_calls' in message_data:
                return f"api:{message_data.get('customer_id')}:{message_data.get('request_id')}:{message_data.get('function_name')}"
                
            # Fallback
            return f"unknown:{hash(safe_json_dumps(message_data))}"
        except Exception as e:
            logger.error(f"Error creating message key: {e}")
            return f"error:{time.time()}:{id(message_data)}"
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove entries older than TTL - THREAD SAFE"""
        cutoff_time = current_time - self._ttl_seconds
        keys_to_remove = [
            key for key, timestamp in list(self._processed_messages.items()) 
            if timestamp < cutoff_time
        ]
        for key in keys_to_remove:
            self._processed_messages.pop(key, None)

# ===== DECORATOR FUNCTIONS =====

def track_all_metrics_unified(request_id: str, customer_id: str,
                             resource_topic: str, token_topic: str, api_topic: str):
    """
    Decorator that tracks all metrics with unified resource calculations.
    Calculates resource metrics once and sends identical data to both API and Kafka.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            execution_id = f"{request_id}_{int(time.time() * 1000000)}"

            # Create a custom resource tracker that won't auto-send (to prevent duplicates)
            class NoAutoSendResourceTracker(AtomicResourceTracker):
                def _send_metrics(self):
                    # Override to prevent automatic sending - we'll handle it manually
                    pass
            
            resource_tracker = NoAutoSendResourceTracker(
                execution_id, customer_id, func.__name__, send_to_kafka=False
            )
            
            # Token and API trackers - send to BOTH destinations
            token_tracker_api = SequentialTokenTracker(
                execution_id + "_api", customer_id, func.__name__, send_to_kafka=False
            )
            token_tracker_kafka = SequentialTokenTracker(
                execution_id + "_kafka", customer_id, func.__name__, send_to_kafka=True, topic=token_topic
            )
            
            api_tracker_api = ThirdPartyAPITracker(
                execution_id + "_api", customer_id, func.__name__, send_to_kafka=False
            )
            api_tracker_kafka = ThirdPartyAPITracker(
                execution_id + "_kafka", customer_id, func.__name__, send_to_kafka=True, kafka_topic=api_topic
            )

            # Execute with all trackers
            with resource_tracker:
                with token_tracker_api:
                    with token_tracker_kafka:
                        with api_tracker_api:
                            with api_tracker_kafka:
                                result = func(*args, **kwargs)

            # Manually send the SAME resource metrics to both destinations
            if hasattr(resource_tracker, '_final_metrics') and resource_tracker._final_metrics:
                resource_metrics = resource_tracker._final_metrics
                
                # Only send if message tracker allows (prevent duplicates)
                if message_tracker.should_send(request_id, func.__name__, "resource_unified"):
                    # Send to API
                    try:
                        send_to_api_sync("/resource-metrics", resource_metrics)
                    except Exception as e:
                        logger.error(f"Failed sending resource metrics to API: {e}")
                    
                    # Send to Kafka (same exact data)
                    try:
                        safe_send_to_kafka(resource_topic, func.__name__, safe_json_dumps(resource_metrics))
                    except Exception as e:
                        logger.error(f"Failed sending resource metrics to Kafka: {e}")

            return result
        return wrapper
    return decorator


def track_token_usage(request_id: str, customer_id: str):
    """Decorator that tracks OpenAI token usage and sends to API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with SequentialTokenTracker(request_id, customer_id, func.__name__, send_to_kafka=False):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def track_resources_db(request_id: str, customer_id: str):
    """Decorator that tracks CPU-seconds and GB-seconds and sends to API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with AtomicResourceTracker(request_id, customer_id, func.__name__, send_to_kafka=False):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def track_resources_kafka(request_id: str, customer_id: str, topic: str):
    """Decorator that tracks CPU-seconds and GB-seconds and sends to Kafka"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with AtomicResourceTracker(request_id, customer_id, func.__name__, send_to_kafka=True):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def track_token_usage_kafka(request_id: str, customer_id: str, topic: str):
    """Decorator that tracks OpenAI token usage and sends to Kafka"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with SequentialTokenTracker(request_id, customer_id, func.__name__, send_to_kafka=True, topic=topic):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def track_api_usage_kafka(request_id: str, customer_id: str, topic: str):
    """Decorator to track third-party API usage and send to Kafka"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThirdPartyAPITracker(request_id, customer_id, func.__name__, send_to_kafka=True, kafka_topic=topic):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def track_api_usage_db(request_id: str, customer_id: str):
    """Decorator to track third-party API usage and send to API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThirdPartyAPITracker(request_id, customer_id, func.__name__, send_to_kafka=False):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def track_all_metrics_db(request_id: str, customer_id: str):
    """Combined decorator that tracks all metrics and sends to API"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use unique execution ID to prevent cross-contamination
            execution_id = f"{request_id}_{int(time.time() * 1000000)}"
            
            # Initialize all trackers
            resource_tracker = AtomicResourceTracker(execution_id, customer_id, func.__name__, send_to_kafka=False)
            token_tracker = SequentialTokenTracker(execution_id, customer_id, func.__name__, send_to_kafka=False)
            api_tracker = ThirdPartyAPITracker(execution_id, customer_id, func.__name__, send_to_kafka=False)
            
            # Execute with all trackers in proper nesting order
            with resource_tracker:
                with token_tracker:
                    with api_tracker:
                        return func(*args, **kwargs)
        return wrapper
    return decorator

def track_all_metrics_kafka(request_id: str, customer_id: str, 
                           resource_topic: str, token_topic: str, api_topic: str):
    """Combined decorator that tracks all metrics and sends to Kafka"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use unique execution ID to prevent cross-contamination
            execution_id = f"{request_id}_{int(time.time() * 1000000)}"
            
            # Initialize all trackers
            resource_tracker = AtomicResourceTracker(execution_id, customer_id, func.__name__, send_to_kafka=True)
            token_tracker = SequentialTokenTracker(execution_id, customer_id, func.__name__, send_to_kafka=True, topic=token_topic)
            api_tracker = ThirdPartyAPITracker(execution_id, customer_id, func.__name__, send_to_kafka=True, kafka_topic=api_topic)
            
            # Execute with all trackers in proper nesting order
            with resource_tracker:
                with token_tracker:
                    with api_tracker:
                        return func(*args, **kwargs)
        return wrapper
    return decorator

# ===== LEGACY FUNCTIONS FOR BACKWARDS COMPATIBILITY =====

def log_token_usage_to_api(request_id: str, customer_id: str, function_name: str, usage: Dict[str, Any]):
    """Legacy function - send token usage to API directly"""
    data = {
        'request_id': request_id,
        'customer_id': customer_id,
        'function_name': function_name,
        'model': usage.get('model'),
        'prompt_tokens': usage.get('prompt_tokens'),
        'completion_tokens': usage.get('completion_tokens'),
        'total_tokens': usage.get('total_tokens'),
        'call_duration': usage.get('call_duration', 0),
    }
    
    send_to_api_sync('/token-usage', data)

def log_token_usage_to_kafka(request_id: str, customer_id: str, function_name: str, 
                            usage: Dict[str, Any], topic: str):
    """Legacy function - send token usage to Kafka directly"""
    message = {
        'customer_id': customer_id,
        'request_id': request_id,
        'function_name': function_name,
        'model': usage['model'],
        'prompt_tokens': usage['prompt_tokens'],
        'completion_tokens': usage['completion_tokens'],
        'total_tokens': usage['total_tokens'],
        'call_duration': usage.get('call_duration', 0),
        'timestamp': time.time()
    }
    
    safe_send_to_kafka(topic, function_name, safe_json_dumps(message))

def log_to_api(request_id: str, customer_id: str, function_name: str, 
               duration: float, cpu_seconds: float, gb_seconds: float, detailed_cpu_metrics: str):
    """Legacy function - send resource metrics to API directly"""
    data = {
        'request_id': request_id,
        'customer_id': customer_id,
        'function_name': function_name,
        'duration_sec': duration,
        'cpu_seconds': cpu_seconds,
        'gb_seconds': gb_seconds,
        'detailed_cpu_metrics': detailed_cpu_metrics,
    }
    
    send_to_api_sync('/resource-metrics', data)

# ===== UTILITY FUNCTIONS =====

def get_process():
    """Get current process for resource tracking"""
    return safe_get_process()

def get_memory_gb(process):
    """Returns memory in GB from RSS (resident set size)"""
    if process is None:
        return 0.0
    try:
        return process.memory_info().rss / (1024 ** 3)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0

# ===== CONSUMER HELPER =====

def process_kafka_message_with_deduplication(message_data: dict, deduplicator: KafkaMessageDeduplicator = None):
    """
    Process Kafka message with built-in deduplication
    Usage in your consumer:
    
    deduplicator = KafkaMessageDeduplicator()
    
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        if not process_kafka_message_with_deduplication(data, deduplicator):
            continue  # Skip duplicate
        # Process the message normally
    """
    if deduplicator is None:
        deduplicator = KafkaMessageDeduplicator()
    
    if deduplicator.is_duplicate(message_data):
        logger.info(f"Duplicate message detected and skipped: {message_data.get('function_name', 'unknown')}")
        return False
    
    return True

# ===== HEALTH CHECK FUNCTION =====

def health_check():
    """
    Validate SDK dependencies and configuration for production deployment
    Returns: (is_healthy: bool, issues: List[str])
    """
    issues = []
    
    try:
        # Check environment variables
        config_test = SDKConfig.from_env()
    except ValueError as e:
        issues.append(f"Configuration error: {e}")
    
    # Check process access
    process = safe_get_process()
    if process is None:
        issues.append("Cannot access process information - resource tracking will be limited")
    
    # Test Kafka connection
    try:
        producer = get_kafka_producer()
        if producer is None:
            issues.append("Failed to create Kafka producer")
    except Exception as e:
        issues.append(f"Kafka connection failed: {e}")
    
    # Test API endpoint
    try:
        api_config = get_api_config()
        # Basic connectivity test (timeout shortened for health check)
        response = requests.get(f"{api_config['base_url']}/health", timeout=5)
    except Exception as e:
        issues.append(f"API endpoint not reachable: {e}")
    
    # Test logging
    try:
        logger.info("SDK health check completed")
    except Exception as e:
        issues.append(f"Logging system error: {e}")
    
    return len(issues) == 0, issues