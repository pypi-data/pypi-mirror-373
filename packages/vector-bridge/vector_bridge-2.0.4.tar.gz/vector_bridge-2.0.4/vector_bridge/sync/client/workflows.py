import hashlib
import json
import sys
import threading
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import wraps
from io import StringIO
from typing import Any

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.workflows import raise_for_workflow_detail
from vector_bridge.schema.workflows import (WorkflowCache, WorkflowCreate,
                                            WorkflowData, WorkflowStatus,
                                            WorkflowUpdate, deserialize_result,
                                            serialize_result)
from vector_bridge.utils import threaded

# Thread-local storage for output capture stacks
local = threading.local()


class ThreadAwareStream:
    """Proxy stream that writes to the current capture stack level"""

    def __init__(self, original):
        self.original = original  # Original system stream (sys.__stdout__/sys.__stderr__)

    def write(self, data):
        stream_type = "stdout" if self.original is sys.__stdout__ else "stderr"
        stack_name = f"capture_stack_{stream_type}"

        # Write to top of stack if available
        if hasattr(local, stack_name):
            stack = getattr(local, stack_name)
            if stack:
                stack[-1].write(data)
                return

        # Fallback to original stream
        self.original.write(data)

    def flush(self):
        self.original.flush()


# Replace standard streams at module load
sys.stdout = ThreadAwareStream(sys.__stdout__)
sys.stderr = ThreadAwareStream(sys.__stderr__)


class CaptureOutput:
    """Context manager that maintains a stack of capture buffers"""

    def __enter__(self):
        # Initialize stacks if they don't exist
        for stream in ["stdout", "stderr"]:
            stack_name = f"capture_stack_{stream}"
            if not hasattr(local, stack_name):
                setattr(local, stack_name, [])

            # Push new buffer to stack
            buffer = StringIO()
            getattr(local, stack_name).append(buffer)

        return self

    def __exit__(self, *args):
        # Pop buffers from both stacks
        for stream in ["stdout", "stderr"]:
            stack_name = f"capture_stack_{stream}"
            stack = getattr(local, stack_name, [])
            if stack:
                stack.pop()

    def get_output(self):
        """Retrieve output from current stack level"""
        output = []
        for stream in ["stdout", "stderr"]:
            stack_name = f"capture_stack_{stream}"
            stack = getattr(local, stack_name, [])
            if stack:
                buffer = stack[-1]
                buffer.seek(0)
                output.append(buffer.read())
        return "".join(output)


class WorkflowClient:
    """Client for workflow endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def add_workflow(self, workflow_create: WorkflowCreate, integration_name: str = None) -> WorkflowData:
        """
        Add new Workflow to the integration.

        Args:
            workflow_create: The Workflow data to create
            integration_name: The name of the Integration

        Returns:
            Created workflow object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/workflow/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=workflow_create.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
        return WorkflowData.model_validate(result)

    def get_workflow(self, workflow_id: str, integration_name: str = None) -> WorkflowData:
        """
        Retrieve Workflow by ID.

        Args:
            workflow_id: The ID of the Workflow
            integration_name: The name of the Integration

        Returns:
            Workflow object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/workflow/{workflow_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
        return WorkflowData.model_validate(result)

    def update_workflow(
        self,
        workflow_id: str,
        created_at: str,
        workflow_update: WorkflowUpdate,
        integration_name: str = None,
    ) -> WorkflowData:
        """
        Update an existing Workflow.

        Args:
            workflow_id: The ID of the Workflow
            workflow_update: The Workflow updates
            integration_name: The name of the Integration

        Returns:
            Updated workflow object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/workflow/{workflow_id}/update"
        params = {
            "integration_name": integration_name,
            "created_at": created_at,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params, json=workflow_update.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
        return WorkflowData.model_validate(result)


def generate_dynamodb_key(workflow_id, method, args, kwargs):
    method_name = method.__name__

    # Convert args to a string-safe format
    args_str = "_".join(map(str, args)) if args else "no_args"

    # Convert kwargs to key-value pairs, sorted for consistency
    kwargs_str = "_".join(f"{k}-{v}" for k, v in sorted(kwargs.items())) if kwargs else "no_kwargs"

    # Ensure no special characters
    key = f"workflow_{workflow_id}_{method_name}_{args_str}_{kwargs_str}"

    # Truncate if necessary (DB keys should not be too long)
    return method_name + "__" + hashlib.sha256(key.encode()).hexdigest()  # Use SHA-256 for long keys


def log_message(message: str, level: str = "INFO"):
    """Helper function for formatted logging with UTC timestamps"""
    timestamp = datetime.now(timezone.utc).isoformat(sep=" ", timespec="milliseconds")
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "STARTED": "🚀",
        "COMPLETED": "🎉",
        "FAILED": "💥",
        "CACHE": "💾",
    }
    symbol = symbols.get(level.upper(), "ℹ️")
    print(f"{timestamp} {symbol} [{level.upper()}] {message}")


# Method-level caching decorator
def cache_result(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        cache_key = generate_dynamodb_key(self.workflow_id, method, args, kwargs)
        method_name = method.__name__

        # Try to get from cache
        cached_data = self.get_cache(cache_key)
        if cached_data and isinstance(cached_data, WorkflowCache):
            if not cached_data.traceback:
                log_message(f"Cache hit for {method_name} [Key: {cache_key[-8:]}]", "CACHE")
                try:
                    # Deserialize the cached result
                    cached_result = json.loads(cached_data.result)
                    return deserialize_result(cached_result)
                except Exception as e:
                    log_message(
                        f"Failed to deserialize cached result for {method_name}: {str(e)}",
                        "WARNING",
                    )
                    # Continue to execute method if deserialization fails

        log_message(f"Cache miss for {method_name} [Key: {cache_key[-8:]}]", "WARNING")

        with CaptureOutput() as output:
            start_time = datetime.now(timezone.utc)
            result = None
            traceback_info = None

            try:
                log_message(f"Executing {method_name}...", "STARTED")
                result = method(self, *args, **kwargs)
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                log_message(f"{method_name} completed in {duration:.3f}s", "SUCCESS")
                return result
            except Exception as e:
                traceback_info = traceback.format_exc()
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                log_message(f"{method_name} failed after {duration:.3f}s: {str(e)}", "ERROR")
                raise
            finally:
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()

                # Serialize the result properly
                try:
                    serialized_result = serialize_result(result)
                    result_json = json.dumps(serialized_result)
                except Exception as e:
                    log_message(
                        f"Failed to serialize result for {method_name}: {str(e)}",
                        "WARNING",
                    )
                    # Fallback to basic JSON serialization
                    try:
                        result_json = json.dumps(result)
                    except:
                        result_json = json.dumps(str(result))

                workflow_cache = WorkflowCache(
                    method_name=method_name,
                    args=list(args),
                    kwargs=kwargs,
                    started_at=start_time.isoformat(),
                    processed_at=end_time.isoformat(),
                    processing_time=duration,
                    logs=output.get_output(),
                    traceback=traceback_info,
                    result=result_json,
                )

                self.set_cache(cache_key, workflow_cache)
                log_message(f"Cached results for {method_name}", "CACHE")

    return wrapper


# Main workflow execution decorator
def workflow_runner(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        cache_key = generate_dynamodb_key(self.workflow_id, method, args, kwargs)
        workflow_name = method.__name__

        # Try to get from cache
        cached_data = self.get_cache(cache_key)
        if cached_data and isinstance(cached_data, WorkflowCache):
            if not cached_data.traceback:
                log_message(f"Workflow cache hit for {workflow_name}", "CACHE")

                try:
                    # Deserialize the cached result
                    cached_result = json.loads(cached_data.result)
                    deserialized_result = deserialize_result(cached_result)

                    # Update cache with current execution metadata
                    with CaptureOutput() as output:
                        start_time = datetime.now(timezone.utc)
                        end_time = datetime.now(timezone.utc)
                        duration = (end_time - start_time).total_seconds()

                        workflow_cache = WorkflowCache(
                            method_name=workflow_name,
                            args=list(args),
                            kwargs=kwargs,
                            started_at=start_time.isoformat(),
                            processed_at=end_time.isoformat(),
                            processing_time=duration,
                            logs=output.get_output(),
                            traceback=None,
                            result=cached_data.result,  # Keep original serialized result
                        )
                        self.set_cache_threaded(cache_key, workflow_cache)
                        self.update_status_threaded(WorkflowStatus.COMPLETED)

                    return deserialized_result

                except Exception as e:
                    log_message(
                        f"Failed to deserialize cached workflow result for {workflow_name}: {str(e)}",
                        "WARNING",
                    )
                    # Continue to execute workflow if deserialization fails

        log_message(f"Workflow cache miss for {workflow_name}", "WARNING")

        with CaptureOutput() as output:
            start_time = datetime.now(timezone.utc)
            result = None
            traceback_info = None

            # Update status to in progress
            self.update_status(WorkflowStatus.IN_PROGRESS)
            log_message(f"Workflow {workflow_name} starting...", "STARTED")

            try:
                result = method(self, *args, **kwargs)
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                self.update_status(WorkflowStatus.COMPLETED)
                log_message(
                    f"Workflow {workflow_name} completed in {duration:.3f}s",
                    "COMPLETED",
                )
                return result
            except Exception as e:
                traceback_info = traceback.format_exc()
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                self.update_status(WorkflowStatus.FAILED)
                log_message(
                    f"Workflow {workflow_name} failed after {duration:.3f}s: {str(e)}",
                    "FAILED",
                )
                raise
            finally:
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()

                # Serialize the result properly
                try:
                    serialized_result = serialize_result(result)
                    result_json = json.dumps(serialized_result)
                except Exception as e:
                    log_message(
                        f"Failed to serialize workflow result for {workflow_name}: {str(e)}",
                        "WARNING",
                    )
                    # Fallback to basic JSON serialization
                    try:
                        result_json = json.dumps(result)
                    except:
                        result_json = json.dumps(str(result))

                workflow_cache = WorkflowCache(
                    method_name=workflow_name,
                    args=list(args),
                    kwargs=kwargs,
                    started_at=start_time.isoformat(),
                    processed_at=end_time.isoformat(),
                    processing_time=duration,
                    logs=output.get_output(),
                    traceback=traceback_info,
                    result=result_json,
                )

                self.set_cache(cache_key, workflow_cache)
                log_message(
                    f"Persisted workflow state for {workflow_name} [Key: {cache_key[-8:]}]",
                    "CACHE",
                )

    return wrapper


class Workflow(ABC):
    """
    Abstract base class for building workflow processes with automatic caching and status tracking.

    This class serves as a foundation for creating workflow implementations that need:
    - Status tracking (pending, in-progress, completed, failed)
    - Automatic caching of intermediate results with support for Pydantic models and dataclasses
    - Output and error capture

    The workflow system now supports:
    - Pydantic models (both v1 and v2)
    - Python dataclasses
    - Regular JSON-serializable objects
    - Complex nested structures (lists, dicts containing the above)

    Usage:
        1. Create a custom class inheriting from Workflow
        2. Implement a main method decorated with @workflow_runner
        3. Implement individual processing steps decorated with @cache_result

    Example:
        from pydantic import BaseModel
        from dataclasses import dataclass

        class UserModel(BaseModel):
            name: str
            age: int

        @dataclass
        class ProcessingResult:
            success: bool
            message: str
            data: dict

        class MyWorkflow(Workflow):
            @workflow_runner
            def run(self, input_data):
                # Main workflow execution
                user = self.fetch_user(input_data)
                result = self.process_user(user)
                return self.generate_report(result)

            @cache_result
            def fetch_user(self, user_id: str) -> UserModel:
                # This result will be cached as a Pydantic model
                return UserModel(name="John Doe", age=30)

            @cache_result
            def process_user(self, user: UserModel) -> ProcessingResult:
                # This result will be cached as a dataclass
                return ProcessingResult(
                    success=True,
                    message=f"Processed user {user.name}",
                    data={"processed_at": datetime.now().isoformat()}
                )

            @cache_result
            def generate_report(self, result: ProcessingResult) -> dict:
                # This result will be cached as a regular dict
                return {"report": result.message, "success": result.success}

        # Usage:
        workflow = MyWorkflow(client, workflow_create)
        result = workflow.run("user123")
    """

    def __init__(self, client: VectorBridgeClient, workflow_create: WorkflowCreate):
        self.client = client
        self.workflow_id = workflow_create.workflow_id
        self.workflow_data: WorkflowData = self.client.workflows.add_workflow(workflow_create)

    @abstractmethod
    def run(self):
        pass

    def refresh(self):
        """Refresh workflow data from the server"""
        self.workflow_data = self.client.workflows.get_workflow(self.workflow_id)

    @threaded
    def update_status_threaded(self, status: WorkflowStatus):
        self.update_status(status)

    def update_status(self, status: WorkflowStatus):
        """Update the workflow status"""
        self.workflow_data = self.client.workflows.update_workflow(
            workflow_id=self.workflow_id,
            created_at=self.workflow_data.created_at,
            workflow_update=WorkflowUpdate(status=status),
        )

    @property
    def status(self) -> WorkflowStatus:
        """Get the current workflow status"""
        return self.workflow_data.status

    def get_cache(self, key: str) -> Any:
        """Get value from workflow cache"""
        if not self.workflow_data.cache:
            return None
        return self.workflow_data.cache.get(key)

    @threaded
    def set_cache_threaded(self, key: str, value: WorkflowCache):
        self.set_cache(key, value)

    def set_cache(self, key: str, value: WorkflowCache):
        """Set value in workflow cache"""
        # Update workflow with new cache using WorkflowUpdate structure
        self.workflow_data = self.client.workflows.update_workflow(
            workflow_id=self.workflow_id,
            created_at=self.workflow_data.created_at,
            workflow_update=WorkflowUpdate(cache={key: value}),
        )
