from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypedDict

from temporalio import workflow as temporal_workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from typing_extensions import NotRequired, Unpack

from .workflow import (
    ChildStart,
    ChildWorkflowCancellationType,
    ParentClosePolicy,
    WorkflowLogger,
)

if TYPE_CHECKING:
    from collections.abc import Callable

log = WorkflowLogger()

get_external_agent_handle = (
    temporal_workflow.get_external_workflow_handle
)
agent_info = temporal_workflow.info
condition = temporal_workflow.wait_condition
import_functions = temporal_workflow.unsafe.imports_passed_through
uuid = temporal_workflow.uuid4
all_events_finished = temporal_workflow.all_handlers_finished

__all__ = [
    "NonRetryableError",
    "RetryPolicy",
    "RetryableError",
    "agent_info",
    "all_events_finished",
    "condition",
    "get_external_agent_handle",
    "import_functions",
    "log",
    "uuid",
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


class Agent:
    def defn(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Define an agent.

        Example:
            .. code-block:: python

                @agent.defn()
                class Agent:
                    @agent.run

        """

        def decorator(cls: type) -> type:
            if description:
                cls.__restack_description__ = description
            return temporal_workflow.defn(
                name=name,
                sandboxed=True,
            )(cls)

        return decorator

    def state(
        self,
        fn: Any,
        name: str | None = None,
        description: str | None = None,
    ) -> Any:
        """Register a method to query an agent state.

        Example:

            .. code-block:: python

                @agent.state
                def current_state(self):
                    return self.state

        Args:
            fn: The agent instance.
            name (str, optional): State name.
            description (str, optional): State description.

        Returns:
            Any: The state data.
        """
        return temporal_workflow.query(
            fn,
            name=name,
            description=description,
        )

    def event(
        self,
        function: RestackFunction,
    ) -> Any:
        """Defines an agent event.

        Example:

            .. code-block:: python

                @agent.event
                async def event_name(self, event_name: EventInput):
                    output_data = await agent.step(
                        function=Function,
                    )
                    return output_data

        Args:
            function: The agent instance.
            event (EventInput): Pydantic model for event input.

        Returns:
            Any: The data returned by the event.
        """
        from functools import wraps

        name = function.__name__

        @wraps(function)
        async def wrapped_handler(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            try:
                return await function(*args, **kwargs)
            except Exception as error:
                error_message = f"Error with restack stream to websocket: {error}"
                raise ApplicationError(error_message) from error

        return temporal_workflow.update(
            wrapped_handler,
            name=name,
        )

    def run(self, function: RestackFunction) -> Any:
        """Defines what happens when the agent runs.

        Example:

            .. code-block:: python

                @agent.defn()
                  class Agent:
                      @agent.run
                      async def run(self, agent_input: AgentInput):
                          await agent.condition(lambda: self.done)
                          return AgentOutput(data=agent_input.data)

        Args:
            function: The agent instance.
            agent_input (AgentInput): The main run method.

        Returns:
            AgentOutput: The result of the agent after its done.
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
                async def run(self, agent_input: AgentInput) -> None
                Please update the run method accordingly.
            """
            raise TypeError(error_message)

        return temporal_workflow.run(wrapper)

    def condition(
        self,
        fn: Callable[[], bool],
        timeout: timedelta | None = None,
    ) -> None:
        """Wait until a condition becomes true.

        Used in agent.run() to keep running until the agent is done.

        Example:

            .. code-block:: python

                await agent.condition(
                    lambda: self.done)
                )
        """
        return temporal_workflow.wait_condition(
            fn,
            timeout=timeout,
        )

    def should_continue_as_new(self) -> bool:
        """Check if the agent should continue as new.

        Example:

            .. code-block:: python

                await agent.should_continue_as_new()
        """
        return temporal_workflow.info().is_continue_as_new_suggested()

    async def agent_continue_as_new(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Resets the agent to start fresh when its history becomes too large.

        This ensures all pending events are completed before the reset,
        preventing any data loss or incomplete operations.

        Call this when your agent will be running for a long time/receving lots of events (Above 2000 events).

        Args:
            *args: Arguments to pass to the agent when it restarts. Typically the same arguments that were passed to the agent when it was started.
            **kwargs: Keyword arguments to pass to the agent when it restarts.
        """
        workflow_info = temporal_workflow.info()
        await temporal_workflow.wait_condition(
            lambda: workflow_info.is_continue_as_new_suggested(),
        )
        await temporal_workflow.wait_condition(
            lambda: all_events_finished(),
        )
        return temporal_workflow.continue_as_new(*args, **kwargs)

    async def step(
        self,
        **kwargs: Unpack[StepKwargs],
    ) -> Any:
        """Execute a function as a step of the agent.

        Example:

        .. code-block:: python

            with import_functions():
            from src.functions.example_function import (
                example_function,
                ExampleFunctionInput,
            )
            result = await agent.step(
                function=Function,
                function_input=FunctionInput(data=input_data),
            )

        Args:
            **kwargs: Keyword arguments for the step execution.
                function (Function): The function to execute.
                function_input(Optional[FunctionInput(BaseModel)]): Input data for the function. Recommended to use a Pydantic model for input validation.
                task_queue (str, optional): Task queue on which the function is executed.
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
            start_to_close_timeout=start_to_close_timeout,
            schedule_to_close_timeout=schedule_to_close_timeout,
            schedule_to_start_timeout=schedule_to_start_timeout,
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

            workflow_result = await agent.child_start(
                workflow=ChildWorkflow,
                workflow_id="child-workflow-123",
                workflow_input=WorkflowInput(data="example"),
            )
            agent_result = await agent.child_start(
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
            if (workflow_input or agent_input)
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

            workflow_result = await agent.child_execute(
                workflow=ChildWorkflow,
                workflow_id="child-workflow-123",
                workflow_input=ChildWorkflowInput(data="example"),
            )
            agent_result = await agent.child_execute(
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
        return await temporal_workflow.execute_child_workflow(
            workflow=workflow or agent,
            args=[workflow_input or agent_input]
            if (workflow_input or agent_input)
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

    async def sleep(self, seconds: int) -> Any:
        """Waits for a set duration.

        Example:

            .. code-block:: python
                await agent.sleep(5)

        Args:
            seconds (int): Time to sleep in seconds.

        Returns:
            None
        """
        return await asyncio.sleep(seconds)

    def _get_engine_id_from_client(self) -> Any:
        return temporal_workflow.memo_value(
            "engineId",
            "local",
            type_hint=str,
        )

    def _add_engine_id_prefix(
        self,
        engine_id: str,
        agent_id: str,
    ) -> str:
        if agent_id.startswith(f"{engine_id}-"):
            return agent_id
        return f"{engine_id}-{agent_id}"


agent = Agent()
