# ruff: noqa: N815
# PlaygroundRun needs consistent typing between frontend, server, typescript and python library

from datetime import timedelta
from typing import Any

from pydantic import BaseModel, Field

from restack_ai.workflow import temporal_workflow, workflow


class PlaygroundInput(BaseModel):
    functionName: str = Field(description="Function to execute.")
    taskQueue: str = Field(
        description="The task queue on which the function will be executed.",
    )
    input: Any | None = Field(
        default=None,
        description="The input to the function, can be any JSON-serializable value.",
    )


@workflow.defn(
    name="playgroundRun",
    description="A playground workflow to execute function from developer UI.",
)
class PlaygroundRun:
    @workflow.run
    async def run(self, params: PlaygroundInput) -> Any:
        engine_id = workflow._get_engine_id_from_client()  # noqa: SLF001
        return await temporal_workflow.execute_activity(
            activity=params.functionName,
            task_queue=f"{engine_id}-{params.taskQueue}",
            args=[params.input],
            start_to_close_timeout=timedelta(seconds=120),
        )


@workflow.defn()
class FunctionsOnly:
    """FunctionsOnly workflow that prevents TaskLocals issues for functions-only services.

    This workflow should never actually be executed - it exists only to
    ensure that workers have at least one workflow registered.
    """

    @workflow.run
    async def run(self) -> str:
        # This should never be called
        return "functions_only_workflow_should_not_be_called"
