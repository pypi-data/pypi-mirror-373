"""
Developer-Friendly Decorators and Utilities

This module provides decorators and utilities to make agent development easier.
"""

import time
import functools
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime

from .exceptions import ValidationError, RateLimitError


def capability(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None,
    returns: Optional[Dict[str, Any]] = None,
    examples: Optional[List[Dict[str, Any]]] = None
):
    """
    Decorator to automatically declare a capability when a method is defined.
    
    Args:
        name: Capability name
        description: What this capability does
        parameters: Expected input parameters schema
        returns: Expected return value schema
        examples: Usage examples
    
    Example:
        >>> class MyAgent(Agent):
        ...     @capability(
        ...         "text_analysis",
        ...         "Analyze text sentiment and extract keywords",
        ...         parameters={"text": {"type": "string", "required": True}},
        ...         returns={"sentiment": {"type": "string"}}
        ...     )
        ...     def analyze_text(self, text: str):
        ...         # Your analysis logic here
        ...         return {"sentiment": "positive"}
    """
    def decorator(func: Callable) -> Callable:
        # Store capability info on the function
        func._capability_spec = {
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "returns": returns or {},
            "examples": examples or []
        }
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Auto-declare capability if agent supports it
            if hasattr(self, 'declare_capability'):
                try:
                    # Check if capability is already declared
                    if not hasattr(self, '_capabilities') or name not in self._capabilities:
                        self.declare_capability(name, description, parameters, returns, examples)
                except Exception as e:
                    # Only ignore if capability already exists
                    if hasattr(self, 'log'):
                        self.log(f"Could not auto-declare capability {name}: {e}", "debug")
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def request_handler(request_type: str):
    """
    Decorator to automatically register a method as a request handler.
    
    Args:
        request_type: Type of request this method handles
    
    Example:
        >>> class MyAgent(Agent):
        ...     @request_handler("calculate")
        ...     def handle_calculation(self, data):
        ...         return {"result": data["a"] + data["b"]}
    """
    def decorator(func: Callable) -> Callable:
        func._request_type = request_type
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Auto-register handler if agent supports it
            if hasattr(self, 'register_handler'):
                try:
                    # Create a wrapper that extracts data from first argument
                    def handler_wrapper(data):
                        return func(self, data)
                    self.register_handler(request_type, handler_wrapper)
                except:
                    pass  # Handler may already be registered
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def validate_input(**field_specs):
    """
    Decorator to validate input parameters against a schema.
    
    Args:
        **field_specs: Field validation specifications
    
    Example:
        >>> @validate_input(
        ...     text={"type": "string", "required": True, "min_length": 1},
        ...     language={"type": "string", "default": "en"},
        ...     confidence={"type": "number", "min": 0, "max": 1}
        ... )
        ... def analyze_text(self, text, language="en", confidence=0.5):
        ...     return {"sentiment": "positive"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get function parameter names
            import inspect
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())[1:]  # Skip 'self'
            
            # Create a dict of all arguments
            all_args = {}
            
            # Add positional arguments
            for i, arg in enumerate(args):
                if i < len(param_names):
                    all_args[param_names[i]] = arg
            
            # Add keyword arguments
            all_args.update(kwargs)
            
            # Validate each field
            validated_args = {}
            for field_name, spec in field_specs.items():
                value = all_args.get(field_name)
                
                # Check required fields
                if spec.get("required", False) and value is None:
                    raise ValidationError(f"Required field '{field_name}' is missing")
                
                # Apply defaults
                if value is None and "default" in spec:
                    value = spec["default"]
                
                # Type validation
                if value is not None:
                    expected_type = spec.get("type")
                    if expected_type:
                        if expected_type == "string" and not isinstance(value, str):
                            raise ValidationError(f"Field '{field_name}' must be a string")
                        elif expected_type == "number" and not isinstance(value, (int, float)):
                            raise ValidationError(f"Field '{field_name}' must be a number")
                        elif expected_type == "integer" and not isinstance(value, int):
                            raise ValidationError(f"Field '{field_name}' must be an integer")
                        elif expected_type == "boolean" and not isinstance(value, bool):
                            raise ValidationError(f"Field '{field_name}' must be a boolean")
                        elif expected_type == "array" and not isinstance(value, list):
                            raise ValidationError(f"Field '{field_name}' must be an array")
                        elif expected_type == "object" and not isinstance(value, dict):
                            raise ValidationError(f"Field '{field_name}' must be an object")
                    
                    # Range validation for numbers
                    if expected_type in ["number", "integer"]:
                        if "min" in spec and value < spec["min"]:
                            raise ValidationError(f"Field '{field_name}' must be >= {spec['min']}")
                        if "max" in spec and value > spec["max"]:
                            raise ValidationError(f"Field '{field_name}' must be <= {spec['max']}")
                    
                    # Length validation for strings/arrays
                    if expected_type in ["string", "array"]:
                        if "min_length" in spec and len(value) < spec["min_length"]:
                            raise ValidationError(f"Field '{field_name}' must have length >= {spec['min_length']}")
                        if "max_length" in spec and len(value) > spec["max_length"]:
                            raise ValidationError(f"Field '{field_name}' must have length <= {spec['max_length']}")
                    
                    # Enum validation
                    if "enum" in spec and value not in spec["enum"]:
                        raise ValidationError(f"Field '{field_name}' must be one of: {spec['enum']}")
                
                validated_args[field_name] = value
            
            # Update kwargs with validated values
            kwargs.update(validated_args)
            
            return func(self, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(requests_per_second: float = 1.0, burst_size: int = 1):
    """
    Decorator to rate limit method calls.
    
    Args:
        requests_per_second: Maximum requests per second
        burst_size: Maximum burst size
    
    Example:
        >>> @rate_limit(requests_per_second=2.0, burst_size=5)
        ... def expensive_operation(self, data):
        ...     # This method will be rate limited
        ...     return process_data(data)
    """
    def decorator(func: Callable) -> Callable:
        last_calls = []
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the time window
            window_start = now - (burst_size / requests_per_second)
            last_calls[:] = [call_time for call_time in last_calls if call_time > window_start]
            
            # Check if we're at the rate limit
            if len(last_calls) >= burst_size:
                sleep_time = (last_calls[0] + (burst_size / requests_per_second)) - now
                if sleep_time > 0:
                    raise RateLimitError(f"Rate limit exceeded. Retry after {sleep_time:.2f} seconds")
            
            # Record this call
            last_calls.append(now)
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_multiplier: float = 2.0):
    """
    Decorator to retry method calls on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
    
    Example:
        >>> @retry_on_failure(max_retries=3, delay=1.0)
        ... def unreliable_operation(self, data):
        ...     # This method will be retried up to 3 times on failure
        ...     return call_external_api(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Log retry attempt if agent has logging
                    if hasattr(self, 'log'):
                        self.log(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...", "warning")
                    
                    # Don't sleep after the last attempt
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
            
            # All retries exhausted
            if hasattr(self, 'log'):
                self.log(f"All {max_retries + 1} attempts failed", "error")
            
            raise last_exception
        
        return wrapper
    return decorator


def timing_stats(include_args: bool = False):
    """
    Decorator to track timing statistics for method calls.
    
    Args:
        include_args: Whether to include argument info in stats
    
    Example:
        >>> @timing_stats(include_args=True)
        ... def slow_operation(self, data):
        ...     # Timing stats will be tracked automatically
        ...     return process_large_dataset(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            
            try:
                result = func(self, *args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Store timing stats if agent supports it
                if hasattr(self, '_timing_stats'):
                    if not hasattr(self, '_timing_stats'):
                        self._timing_stats = {}
                    
                    if method_name not in self._timing_stats:
                        self._timing_stats[method_name] = {
                            "call_count": 0,
                            "total_time": 0,
                            "avg_time": 0,
                            "min_time": float('inf'),
                            "max_time": 0,
                            "success_count": 0,
                            "failure_count": 0
                        }
                    
                    stats = self._timing_stats[method_name]
                    stats["call_count"] += 1
                    stats["total_time"] += duration
                    stats["avg_time"] = stats["total_time"] / stats["call_count"]
                    stats["min_time"] = min(stats["min_time"], duration)
                    stats["max_time"] = max(stats["max_time"], duration)
                    
                    if success:
                        stats["success_count"] += 1
                    else:
                        stats["failure_count"] += 1
                
                # Log timing info if agent has logging
                if hasattr(self, 'log'):
                    status = "SUCCESS" if success else "FAILED"
                    arg_info = f" with args: {args}, kwargs: {kwargs}" if include_args else ""
                    self.log(f"{method_name} {status} in {duration:.3f}s{arg_info}", "debug")
            
            return result
        
        return wrapper
    return decorator


def cache_result(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache method results for a specified time.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        key_func: Function to generate cache key from arguments
    
    Example:
        >>> @cache_result(ttl_seconds=600)  # Cache for 10 minutes
        ... def expensive_calculation(self, x, y):
        ...     time.sleep(5)  # Simulate expensive operation
        ...     return x ** y
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key from args and kwargs
                cache_key = str(args) + str(sorted(kwargs.items()))
            
            now = time.time()
            
            # Check if we have a valid cached result
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if now - timestamp < ttl_seconds:
                    if hasattr(self, 'log'):
                        self.log(f"Cache hit for {func.__name__}", "debug")
                    return result
            
            # Cache miss or expired - call the function
            if hasattr(self, 'log'):
                self.log(f"Cache miss for {func.__name__}", "debug")
            
            result = func(self, *args, **kwargs)
            cache[cache_key] = (result, now)
            
            # Clean up old cache entries
            expired_keys = [k for k, (_, ts) in cache.items() if now - ts >= ttl_seconds]
            for k in expired_keys:
                del cache[k]
            
            return result
        
        return wrapper
    return decorator


def log_calls(level: str = "info", include_args: bool = False, include_result: bool = False):
    """
    Decorator to log method calls.
    
    Args:
        level: Log level (info, debug, warning, error)
        include_args: Whether to log arguments
        include_result: Whether to log return value
    
    Example:
        >>> @log_calls(level="debug", include_args=True)
        ... def important_method(self, data):
        ...     return {"processed": True}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            method_name = func.__name__
            
            # Log method call
            if hasattr(self, 'log'):
                msg = f"Calling {method_name}"
                if include_args:
                    msg += f" with args: {args}, kwargs: {kwargs}"
                self.log(msg, level)
            
            try:
                result = func(self, *args, **kwargs)
                
                # Log successful completion
                if hasattr(self, 'log'):
                    msg = f"Completed {method_name}"
                    if include_result:
                        msg += f" -> {result}"
                    self.log(msg, level)
                
                return result
                
            except Exception as e:
                # Log exception
                if hasattr(self, 'log'):
                    self.log(f"Exception in {method_name}: {e}", "error")
                raise
        
        return wrapper
    return decorator