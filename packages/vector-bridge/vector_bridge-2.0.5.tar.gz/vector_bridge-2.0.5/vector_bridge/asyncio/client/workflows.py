import asyncio
import hashlib
import json
import sys
import traceback
from abc import ABC, abstractmethod
# Context variable for output capture (async-safe alternative to threading.local)
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from io import StringIO
from typing import Any

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.workflows import raise_for_workflow_detail
from vector_bridge.schema.workflows import (WorkflowCache, WorkflowCreate,
                                            WorkflowData, WorkflowStatus,
                                            WorkflowUpdate, deserialize_result,
                                            serialize_result)

capture_stack_stdout: ContextVar = ContextVar("capture_stack_stdout", default=[])
capture_stack_stderr: ContextVar = ContextVar("capture_stack_stderr", default=[])


class AsyncThreadAwareStream:
    """Async-safe proxy stream that writes to the current capture stack level"""

    def __init__(self, original):
        self.original = original

    def write(self, data):
        stream_name = "stdout" if self.original is sys.__stdout__ else "stderr"
        context_var = capture_stack_stdout if stream_name == "stdout" else capture_stack_stderr

        try:
            stack = context_var.get()
            if stack:
                stack[-1].write(data)
                return
        except LookupError:
            pass

        # Fallback to original stream
        self.original.write(data)

    def flush(self):
        self.original.flush()


# Only replace streams if they haven't been replaced already
if not isinstance(sys.stdout, AsyncThreadAwareStream):
    sys.stdout = AsyncThreadAwareStream(sys.__stdout__)
if not isinstance(sys.stderr, AsyncThreadAwareStream):
    sys.stderr = AsyncThreadAwareStream(sys.__stderr__)


class AsyncCaptureOutput:
    """Async-safe context manager that maintains a stack of capture buffers"""

    def __enter__(self):
        # Get current stacks or create empty ones
        try:
            stdout_stack = capture_stack_stdout.get().copy()
        except LookupError:
            stdout_stack = []

        try:
            stderr_stack = capture_stack_stderr.get().copy()
        except LookupError:
            stderr_stack = []

        stdout_buffer = StringIO()
        stderr_buffer = StringIO()

        stdout_stack.append(stdout_buffer)
        stderr_stack.append(stderr_buffer)

        self.stdout_token = capture_stack_stdout.set(stdout_stack)
        self.stderr_token = capture_stack_stderr.set(stderr_stack)

        return self

    def __exit__(self, *args):
        # Reset context variables to previous state
        capture_stack_stdout.reset(self.stdout_token)
        capture_stack_stderr.reset(self.stderr_token)

    def get_output(self):
        """Retrieve output from current stack level"""
        output = []
        try:
            stdout_stack = capture_stack_stdout.get()
            stderr_stack = capture_stack_stderr.get()

            if stdout_stack:
                stdout_buffer = stdout_stack[-1]
                stdout_buffer.seek(0)
                output.append(stdout_buffer.read())

            if stderr_stack:
                stderr_buffer = stderr_stack[-1]
                stderr_buffer.seek(0)
                output.append(stderr_buffer.read())
        except LookupError:
            pass

        return "".join(output)


class AsyncWorkflowClient:
    """Async client for workflow endpoints that require an API key."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def add_workflow(self, workflow_create: WorkflowCreate, integration_name: str = None) -> WorkflowData:
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

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/workflow/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url, headers=headers, params=params, json=workflow_create.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
            return WorkflowData.model_validate(result)

    async def get_workflow(self, workflow_id: str, integration_name: str = None) -> WorkflowData:
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

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/workflow/{workflow_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
            return WorkflowData.model_validate(result)

    async def update_workflow(
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
            created_at: The creation timestamp
            workflow_update: The Workflow updates
            integration_name: The name of the Integration

        Returns:
            Updated workflow object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/workflow/{workflow_id}/update"
        params = {
            "integration_name": integration_name,
            "created_at": created_at,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.put(
            url, headers=headers, params=params, json=workflow_update.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
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


# Async method-level caching decorator
def async_cache_result(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        cache_key = generate_dynamodb_key(self.workflow_id, method, args, kwargs)
        method_name = method.__name__

        # Try to get from cache
        cached_data = await self.get_cache(cache_key)
        if cached_data and isinstance(cached_data, WorkflowCache):
            if not cached_data.traceback:
                log_message(f"Cache hit for {method_name} [Key: {cache_key[-8:]}]", "CACHE")
                try:
                    # Deserialize the cached result
                    cached_result = (
                        json.loads(cached_data.result) if isinstance(cached_data.result, str) else cached_data.result
                    )
                    return deserialize_result(cached_result)
                except Exception as e:
                    log_message(
                        f"Failed to deserialize cached result for {method_name}: {str(e)}",
                        "WARNING",
                    )
                    # Continue to execute method if deserialization fails

        log_message(f"Cache miss for {method_name} [Key: {cache_key[-8:]}]", "WARNING")

        with AsyncCaptureOutput() as output:
            start_time = datetime.now(timezone.utc)
            result = None
            traceback_info = None

            try:
                log_message(f"Executing {method_name}...", "STARTED")
                result = await method(self, *args, **kwargs)
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

                await self.set_cache(cache_key, workflow_cache)
                log_message(f"Cached results for {method_name}", "CACHE")

    return wrapper


# Async main workflow execution decorator
def async_workflow_runner(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        cache_key = generate_dynamodb_key(self.workflow_id, method, args, kwargs)
        workflow_name = method.__name__

        # Try to get from cache
        cached_data = await self.get_cache(cache_key)
        if cached_data and isinstance(cached_data, WorkflowCache):
            if not cached_data.traceback:
                log_message(f"Workflow cache hit for {workflow_name}", "CACHE")

                try:
                    # Deserialize the cached result
                    cached_result = (
                        json.loads(cached_data.result) if isinstance(cached_data.result, str) else cached_data.result
                    )
                    deserialized_result = deserialize_result(cached_result)

                    # Update cache with current execution metadata
                    with AsyncCaptureOutput() as output:
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
                        # Use background task for cache update
                        asyncio.create_task(self.set_cache(cache_key, workflow_cache))
                        asyncio.create_task(self.update_status(WorkflowStatus.COMPLETED))

                    return deserialized_result

                except Exception as e:
                    log_message(
                        f"Failed to deserialize cached workflow result for {workflow_name}: {str(e)}",
                        "WARNING",
                    )
                    # Continue to execute workflow if deserialization fails

        log_message(f"Workflow cache miss for {workflow_name}", "WARNING")

        with AsyncCaptureOutput() as output:
            start_time = datetime.now(timezone.utc)
            result = None
            traceback_info = None

            # Update status to in progress
            await self.update_status(WorkflowStatus.IN_PROGRESS)
            log_message(f"Workflow {workflow_name} starting...", "STARTED")

            try:
                result = await method(self, *args, **kwargs)
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                await self.update_status(WorkflowStatus.COMPLETED)
                log_message(
                    f"Workflow {workflow_name} completed in {duration:.3f}s",
                    "COMPLETED",
                )
                return result
            except Exception as e:
                traceback_info = traceback.format_exc()
                duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                await self.update_status(WorkflowStatus.FAILED)
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

                await self.set_cache(cache_key, workflow_cache)
                log_message(
                    f"Persisted workflow state for {workflow_name} [Key: {cache_key[-8:]}]",
                    "CACHE",
                )

    return wrapper


class AsyncWorkflow(ABC):
    """
    Abstract base class for building async workflow processes with automatic caching and status tracking.

    This class serves as a foundation for creating async workflow implementations that need:
    - Status tracking (pending, in-progress, completed, failed)
    - Automatic caching of intermediate results with support for Pydantic models and dataclasses
    - Output and error capture

    The async workflow system supports:
    - Pydantic models (both v1 and v2)
    - Python dataclasses
    - Regular JSON-serializable objects
    - Complex nested structures (lists, dicts containing the above)

    Usage:
        1. Create a custom class inheriting from AsyncWorkflow
        2. Implement a main method decorated with @async_workflow_runner
        3. Implement individual processing steps decorated with @async_cache_result

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

        class MyAsyncWorkflow(AsyncWorkflow):
            @async_workflow_runner
            async def run(self, input_data):
                # Main workflow execution
                user = await self.fetch_user(input_data)
                result = await self.process_user(user)
                return await self.generate_report(result)

            @async_cache_result
            async def fetch_user(self, user_id: str) -> UserModel:
                # This result will be cached as a Pydantic model
                return UserModel(name="John Doe", age=30)

            @async_cache_result
            async def process_user(self, user: UserModel) -> ProcessingResult:
                # This result will be cached as a dataclass
                return ProcessingResult(
                    success=True,
                    message=f"Processed user {user.name}",
                    data={"processed_at": datetime.now().isoformat()}
                )

            @async_cache_result
            async def generate_report(self, result: ProcessingResult) -> dict:
                # This result will be cached as a regular dict
                return {"report": result.message, "success": result.success}

        # Usage:
        async with AsyncVectorBridgeClient() as client:
            await client.login("user@example.com", "password")
            workflow = MyAsyncWorkflow(client, workflow_create)
            await workflow.initialize()
            result = await workflow.run("user123")
    """

    def __init__(self, client: AsyncVectorBridgeClient, workflow_create: WorkflowCreate):
        self.client = client
        self.workflow_id = workflow_create.workflow_id
        self._workflow_create = workflow_create
        self.workflow_data: WorkflowData = None

    async def initialize(self):
        """Initialize the workflow data (call this after creating the instance)"""
        if self.workflow_data is None:
            self.workflow_data = await self.client.workflows.add_workflow(self._workflow_create)

    @abstractmethod
    async def run(self):
        """Abstract method that must be implemented by subclasses"""
        pass

    async def refresh(self):
        """Refresh workflow data from the server"""
        self.workflow_data = await self.client.workflows.get_workflow(self.workflow_id)

    async def update_status(self, status: WorkflowStatus):
        """Update the workflow status"""
        if self.workflow_data is None:
            await self.initialize()

        self.workflow_data = await self.client.workflows.update_workflow(
            workflow_id=self.workflow_id,
            created_at=self.workflow_data.created_at,
            workflow_update=WorkflowUpdate(status=status),
        )

    @property
    def status(self) -> WorkflowStatus:
        """Get the current workflow status"""
        return self.workflow_data.status if self.workflow_data else None

    async def get_cache(self, key: str) -> Any:
        """Get value from workflow cache"""
        if self.workflow_data is None:
            await self.initialize()

        if not self.workflow_data or not self.workflow_data.cache:
            return None
        return self.workflow_data.cache.get(key)

    async def set_cache(self, key: str, value: WorkflowCache):
        """Set value in workflow cache"""
        if self.workflow_data is None:
            await self.initialize()

        # Update workflow with new cache using WorkflowUpdate structure
        self.workflow_data = await self.client.workflows.update_workflow(
            workflow_id=self.workflow_id,
            created_at=self.workflow_data.created_at,
            workflow_update=WorkflowUpdate(cache={key: value}),
        )
