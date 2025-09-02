from __future__ import annotations
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    finished: bool = False
    status_text: str  # running idea 4 out of 10: add_more_generations. graph in the info
    info: dict = Field(default_factory=dict)  # a free dict which is sent to the agent
    baseline_code: CodeVersion | None = None
    population: list[CodeVersion] = Field(default_factory=list)  # Each workflow has its own evolutionary population
    best_code_version: CodeVersion | None = None
    best_kpi: float | None = None
    kpis: list[float] = Field(default_factory=list)
    population_size: int | None = None
    num_islands: int | None = None
    max_retries: int = 3  # System-wide retry policy
    user_context_summary: str | None = None

class WorkflowState(BaseModel):
    workflow: Workflow
    system_info: SystemInfo | None = None
    current_failed_code: CodeVersion | None = None  # Current failed code awaiting retry



class CodeVersion(BaseModel):
    code_version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # baseline / more_generations / try_blah_blah
    idea: str
    code: str
    info: dict = Field(
        default_factory=dict)  # a free dict which is sent to the agent, should contain descriptions and other info
    result: CodeResult | None = None
    is_final: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    parent_code_version_id: str | None = None
    retry_count: int = 0  # Number of times this code has been retried
    # Hypothesis support (must match engine)
    hypothesis: str | None = None
    hypothesis_outcome: str | None = None  # "supported" | "refuted" | "inconclusive"

class CodeResult(BaseModel):
    runtime_ms: float = 0
    return_code: int
    stdout: str | None = None
    stderr: str | None = None
    kpi: float | None = None
    is_good: bool | None = None


class EngineType(str, Enum):
    MOCK = 'MOCK'
    CO_DATASCIENTIST = 'CO_DATASCIENTIST'
    EVOLVE = 'EVOLVE'
    EVOLVE_HYPOTHESIS = 'EVOLVE_HYPOTHESIS'


class SystemInfo(BaseModel):
    python_libraries: list[str] = Field(default_factory=list)
    python_version: str = ""
    os: str = ""
    # agent_version
    # gpu
    # cpu
    # MORE
#### THIS IS NOT USED!!! just for now to avoid crashing...

# class Prompt(BaseModel):
#     code: str
#     system_prompt: str = "you are a data scientist"
#     task_description: str = "improve the given code using the metrics defined in the code"
#     training_data_format: str = "no training data"
#     current_limitations: str = "no limitations"


