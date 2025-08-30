from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, TypedDict

from temporalio import workflow as temporal_workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import (
    ChildWorkflowCancellationType,
    ParentClosePolicy,
)
from typing_extensions import NotRequired, Unpack

from .observability import log_with_context, logger

temporal_workflow.logger.logger = logger


@dataclass
class ChildStart:
    id: str
    run_id: str


class WorkflowLogger:
    """Enables consistent formatting for workflow logs."""

    def __init__(self) -> None:
        self._logger = temporal_workflow.logger

    def _log(
        self,
        level: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        if temporal_workflow._Runtime.maybe_current():  # noqa: SLF001
            getattr(self._logger, level)(
                message,
                extra={
                    "extra_fields": {
                        **kwargs,
                        "client_log": True,
                    },
                },
            )
        else:
            log_with_context(level.upper(), message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("critical", message, **kwargs)


log = WorkflowLogger()

get_external_workflow_handle = (
    temporal_workflow.get_external_workflow_handle
)
workflow_info = temporal_workflow.info
continue_as_new = temporal_workflow.continue_as_new
import_functions = temporal_workflow.unsafe.imports_passed_through
uuid = temporal_workflow.uuid4

__all__ = [
    "NonRetryableError",
    "RetryPolicy",
    "RetryableError",
    "continue_as_new",
    "get_external_workflow_handle",
    "import_functions",
    "log",
    "uuid",
    "workflow_info",
]

RestackFunction = Any
RestackFunctionInput = Any


class NonRetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=True)


class RetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=False)


class StepKwargs(TypedDict):
    function: RestackFunction
    function_input: NotRequired[RestackFunctionInput]
    task_queue: NotRequired[str]
    retry_policy: NotRequired[RetryPolicy]
    schedule_to_close_timeout: NotRequired[timedelta]


class ChildKwargs(TypedDict, total=False):
    workflow: Any
    workflow_id: str
    workflow_input: Any
    agent: Any
    agent_id: str
    agent_input: Any
    task_queue: str
    cancellation_type: ChildWorkflowCancellationType
    parent_close_policy: ParentClosePolicy
    execution_timeout: timedelta


class Workflow:
    def defn(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Defines a workflow.

        Example:

        .. code-block:: python

            @workflow.defn()
            class Workflow:
                @worfklow.run

        """

        def decorator(cls: type) -> type:
            if description:
                cls.__restack_description__ = description
            return temporal_workflow.defn(
                name=name,
                sandboxed=True,
            )(cls)

        return decorator

    def run(self, function: RestackFunction) -> Any:
        """Defines what happens when the workflow runs.

        Example:

        .. code-block:: python

            @workflow.defn()
            class Workflow:
                @workflow.run
                async def run(
                    self, workflow_input: WorkflowInput
                ) -> WorkflowOutput:
                    result = await workflow.step(
                        function=example_function,
                    )

                return result

        Args:
            function: The workflow instance
            workflow_input (WorkflowInput): The input data for the workflow. Pydantic model recommended.

        Returns:
            WorkflowOutput: The result of the workflow.

        """
        import inspect
        from functools import wraps

        sig = inspect.signature(function)
        expected_params = len(sig.parameters) - 1

        @wraps(function)
        async def wrapper(*args: Any, **_kwargs: Any) -> Any:
            if expected_params == 0:
                return await function(args[0])
            if expected_params == 1:
                return await function(
                    args[0],
                    args[1] if len(args) > 1 else None,
                )
            error_message = """
                Invalid run method signature: the run method must be defined as either:
                async def run(self) -> None
                or:
                async def run(self, workflow_input: WorkflowInput) -> None
                Please update the run method accordingly.
            """
            raise TypeError(error_message)

        return temporal_workflow.run(wrapper)

    async def step(
        self,
        **kwargs: Unpack[StepKwargs],
    ) -> Any:
        """Execute a function as a step of the workflow.

        Example:

        .. code-block:: python

            with import_functions():
                from src.functions.example_function import (
                    example_function,
                    ExampleFunctionInput,
                )
            result = await workflow.step(
                function=example_function,
                function_input=ExampleFunctionInput(text="Hello world"),
            )

        Args:
            **kwargs: Keyword arguments for the step execution.
                function (Function): The function to execute.
                function_input (Optional[FunctionInput(BaseModel)]): Input data for the function. Recommended to use a Pydantic model for input validation.
                task_queue (Optional[str]): Task queue on which the function is executed.
                retry_policy (Optional[RetryPolicy]): Configure how the function should be retried when failing.
                start_to_close_timeout (Optional[timedelta]): Force function to timeout within the given duration. Default 5 minutes.

        Returns:
            FunctionOutput: The result of the function.

        """
        function = kwargs.get("function")
        function_input = kwargs.get("function_input")
        task_queue = kwargs.get("task_queue", "restack")
        retry_policy = kwargs.get("retry_policy")
        schedule_to_close_timeout = kwargs.get(
            "schedule_to_close_timeout",
        )
        schedule_to_start_timeout = kwargs.get(
            "schedule_to_start_timeout",
        )
        start_to_close_timeout = kwargs.get(
            "start_to_close_timeout",
            timedelta(minutes=5),
        )
        heartbeat_timeout = kwargs.get("heartbeat_timeout")
        engine_id = self._get_engine_id_from_client()
        return await temporal_workflow.execute_activity(
            activity=function,
            args=(function_input,)
            if function_input is not None
            else (),
            task_queue=f"{engine_id}-{task_queue}",
            schedule_to_close_timeout=schedule_to_close_timeout,
            schedule_to_start_timeout=schedule_to_start_timeout,
            start_to_close_timeout=start_to_close_timeout,
            heartbeat_timeout=heartbeat_timeout,
            retry_policy=retry_policy,
        )

    async def child_start(
        self,
        **kwargs: Unpack[ChildKwargs],
    ) -> ChildStart:
        """Start a child agent or workflow.

        Example:

        .. code-block:: python

            from .workflow.child import ChildWorkflow, ChildWorkflowInput
            from .agent.child import ChildAgent, ChildAgentInput

            workflow_result = await workflow.child_start(
                workflow=ChildWorkflow,
                workflow_id="child-workflow-123",
                workflow_input=WorkflowInput(data="example"),
            )
            agent_result = await workflow.child_start(
                agent=ChildAgent,
                agent_id="child-agent-123",
                agent_input=AgentInput(data="example"),
            )

        Args(required):
            # For child workflows
            workflow: The child workflow to start.
            workflow_id: A unique identifier for the child workflow.
            workflow_input: The input data for the child workflow. Pydantic model recommended.
            # For child agents
            agent: The child agent to start.
            agent_id: A unique identifier for the child agent.
            agent_input: The input data for the child agent. Pydantic model recommended.

        Args(optional):
            task_queue (str): The task queue for executing the child.
            parent_close_policy (ParentClosePolicy): Specifies the behavior when the parent is closed.
            execution_timeout (timedelta): The maximum duration allowed for the child to complete.

        Returns:
            id: The ID of the child.
            run_id: The ID of the first run of the child.

        """
        workflow = kwargs.get("workflow")
        workflow_input = kwargs.get("workflow_input")
        workflow_id = kwargs.get("workflow_id")
        agent = kwargs.get("agent")
        agent_input = kwargs.get("agent_input")
        agent_id = kwargs.get("agent_id")
        task_queue = kwargs.get("task_queue", "restack")
        cancellation_type = kwargs.get(
            "cancellation_type",
            ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
        parent_close_policy = kwargs.get(
            "parent_close_policy",
            ParentClosePolicy.TERMINATE,
        )
        execution_timeout = kwargs.get("execution_timeout")

        if not workflow and not agent:
            error_message = (
                "Either workflow or agent must be provided."
            )
            log.error(error_message)
            raise ValueError(error_message)
        if workflow and agent:
            error_message = "Either workflow or agent must be provided, not both."
            log.error(error_message)
            raise ValueError(error_message)

        engine_id = self._get_engine_id_from_client()
        is_agent = workflow is None
        handle = await temporal_workflow.start_child_workflow(
            workflow=workflow or agent,
            args=[workflow_input or agent_input]
            if workflow_input or agent_input
            else [],
            id=self._add_engine_id_prefix(
                engine_id,
                workflow_id or agent_id,
            ),
            task_queue=f"{engine_id}-{task_queue}",
            memo={"engineId": engine_id, "agent": is_agent},
            search_attributes={"engineId": [engine_id]},
            cancellation_type=cancellation_type,
            parent_close_policy=parent_close_policy,
            execution_timeout=execution_timeout,
        )

        return ChildStart(
            id=handle.id,
            run_id=handle.first_execution_run_id,
        )

    async def child_execute(
        self,
        **kwargs: Unpack[ChildKwargs],
    ) -> Any:
        """Start a child workflow or agent and wait for it to complete.

        Example:

        .. code-block:: python

            from .workflow.child import ChildWorkflow, ChildWorkflowInput
            from .agent.child import ChildAgent, ChildAgentInput

            workflow_result = await workflow.child_execute(
                workflow=ChildWorkflow,
                workflow_id="child-workflow-123",
                workflow_input=ChildWorkflowInput(data="example"),
            )
            agent_result = await workflow.child_execute(
                agent=ChildAgent,
                agent_id="child-agent-123",
                agent_input=ChildAgentInput(data="example"),
            )

        Args(required):
            # For a child workflow
            workflow: The child workflow class to execute.
            workflow_id: A unique identifier for the child workflow.
            workflow_input: The input data for the child workflow. Pydantic model recommended.
            # For a child agent
            agent: The child agent class to execute.
            agent_id: A unique identifier for the child agent.
            agent_input: The input data for the child agent. Pydantic model recommended.

        Args(optional):
            task_queue (str): The task queue for executing the child.
            parent_close_policy (ParentClosePolicy): Specifies the behavior when the parent is closed.
            execution_timeout (timedelta): The maximum duration allowed for the child to complete.

        Returns:
            Any: The result of the child workflow or agent.

        """
        workflow = kwargs.get("workflow")
        workflow_id = kwargs.get("workflow_id")
        workflow_input = kwargs.get("workflow_input")
        agent = kwargs.get("agent")
        agent_id = kwargs.get("agent_id")
        agent_input = kwargs.get("agent_input")
        task_queue = kwargs.get("task_queue", "restack")
        cancellation_type = kwargs.get(
            "cancellation_type",
            ChildWorkflowCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
        parent_close_policy = kwargs.get(
            "parent_close_policy",
            ParentClosePolicy.TERMINATE,
        )
        execution_timeout = kwargs.get("execution_timeout")
        if not workflow and not agent:
            error_message = (
                "Either workflow or agent must be provided."
            )
            log.error(error_message)
            raise ValueError(error_message)
        if workflow and agent:
            error_message = "Either workflow or agent must be provided, but not both."
            log.error(error_message)
            raise ValueError(error_message)

        engine_id = self._get_engine_id_from_client()
        is_agent = workflow is None
        return await temporal_workflow.execute_child_workflow(
            workflow=workflow or agent,
            args=[workflow_input or agent_input]
            if workflow_input or agent_input
            else [],
            id=self._add_engine_id_prefix(
                engine_id,
                workflow_id or agent_id,
            ),
            task_queue=f"{engine_id}-{task_queue}",
            memo={"engineId": engine_id, "agent": is_agent},
            search_attributes={"engineId": [engine_id]},
            cancellation_type=cancellation_type,
            parent_close_policy=parent_close_policy,
            execution_timeout=execution_timeout,
        )

    async def sleep(self, seconds: int) -> None:
        """Waits for a set duration.

        Example:

        .. code-block:: python

            await workflow.sleep(5)

        Args:
            seconds (int): Time to sleep in seconds.

        Returns:
            None
        """
        return await asyncio.sleep(seconds)

    def _get_engine_id_from_client(self) -> str:
        try:
            return temporal_workflow.memo_value(
                "engineId",
                "local",
                type_hint=str,
            )
        except KeyError:
            return "local"

    def _add_engine_id_prefix(
        self,
        engine_id: str,
        workflow_id: str,
    ) -> str:
        if workflow_id.startswith(f"{engine_id}-"):
            return workflow_id
        return f"{engine_id}-{workflow_id}"


workflow = Workflow()
