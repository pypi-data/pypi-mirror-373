import httpx
import logging
from pydantic import BaseModel

from .models import Workflow, CodeVersion, SystemInfo, CodeResult
from .settings import settings


class CoDatascientistBackendResponse(BaseModel):
    workflow: Workflow
    code_to_run: CodeVersion | None = None


class CoDatascientistBatchResponse(BaseModel):
    workflow: Workflow
    batch_to_run: list[CodeVersion] | None = None
    batch_id: str

class PreflightResponse(BaseModel):
    workflow: Workflow
    questions: list[str]
    observation: str | None = None
    raw_text: str | None = None


async def test_connection() -> str:
    return await _call_co_datascientist_client("/test_connection", {})


async def start_preflight(code: str, system_info: SystemInfo) -> PreflightResponse:
    payload: dict = {"code": code, "system_info": system_info.model_dump()}
    response = await _call_co_datascientist_client("/start_preflight", payload)
    return PreflightResponse.model_validate(response)

async def complete_preflight(workflow_id: str, answers: list[str]) -> CoDatascientistBackendResponse:
    payload = {"workflow_id": workflow_id, "answers": answers}
    response = await _call_co_datascientist_client("/complete_preflight", payload)
    return CoDatascientistBackendResponse.model_validate(response)

async def start_workflow(code: str, system_info: SystemInfo) -> CoDatascientistBackendResponse:
    payload: dict = {"code": code, "system_info": system_info.model_dump()}
    response = await _call_co_datascientist_client("/start_workflow", payload)
    return CoDatascientistBackendResponse.model_validate(response)

async def finished_running_code(
    workflow_id: str,
    code_version: CodeVersion,
    result: CodeResult,
    kpi_value: float | None = None,
) -> CoDatascientistBackendResponse:
    """Notify backend that a program finished running and get next code to run."""
    payload = {
        "workflow_id": workflow_id,
        "code_version": code_version.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
        "kpi_value": kpi_value,
    }
    response = await _call_co_datascientist_client("/finished_running_code", payload)
    return CoDatascientistBackendResponse.model_validate(response)


async def get_batch_to_run(workflow_id: str, batch_size: int | None = None) -> CoDatascientistBatchResponse:
    payload: dict = {"workflow_id": workflow_id}
    if batch_size is not None:
        payload["batch_size"] = batch_size
    response = await _call_co_datascientist_client("/get_batch_to_run", payload)
    return CoDatascientistBatchResponse.model_validate(response)


async def finished_running_batch(
    workflow_id: str,
    batch_id: str,
    results: list[tuple[str, CodeResult]]
) -> CoDatascientistBatchResponse:
    payload = {
        "workflow_id": workflow_id,
        "batch_id": batch_id,
        "results": [
            {"code_version_id": code_version_id, "result": result.model_dump(mode="json")}
            for code_version_id, result in results
        ],
    }
    response = await _call_co_datascientist_client("/finished_running_batch", payload)
    return CoDatascientistBatchResponse.model_validate(response)


async def stop_workflow(workflow_id: str) -> None:
    await _call_co_datascientist_client("/stop_workflow", {"workflow_id": workflow_id})



# Cost tracking helpers (unchanged)
async def get_user_costs() -> dict:
    """Get detailed costs for the authenticated user"""
    return await _call_co_datascientist_client("/user/costs", {})


async def get_user_costs_summary() -> dict:
    """Get summary costs for the authenticated user"""
    return await _call_co_datascientist_client("/user/costs/summary", {})


async def get_user_usage_status() -> dict:
    """Get usage status including remaining money and limits"""
    return await _call_co_datascientist_client("/user/usage_status", {})


async def get_workflow_costs(workflow_id: str) -> dict:
    """Get costs for a specific workflow"""
    return await _call_co_datascientist_client(f"/user/costs/workflow/{workflow_id}", {})


async def get_workflow_population_best(workflow_id: str) -> dict:
    """Fetch best code version KPI for a workflow's current population."""
    return await _call_co_datascientist_client(f"/workflow/{workflow_id}/population/best", {})


async def _call_co_datascientist_client(path, data):
    # Ensure API key is available before making the request
    if not settings.api_key.get_secret_value():
        settings.get_api_key()
    
    url = settings.backend_url + path
    logging.info(f"Dev mode: {settings.dev_mode}")
    logging.info(f"Backend URL: {settings.backend_url}")
    logging.info(f"Making request to: {url}")
    logging.info(f"Request data keys: {list(data.keys()) if data else 'No data'}")
    
    # Prepare headers
    headers = {"Authorization": f"Bearer {settings.api_key.get_secret_value()}"}
    
    # Add OpenAI key header if available
    openai_key = settings.get_openai_key(prompt_if_missing=False)
    if openai_key:
        headers["X-OpenAI-Key"] = openai_key
        logging.info("Including user OpenAI key in request")
    else:
        logging.info("No user OpenAI key - using TropiFlow's free tier")
    
    try:
        async with httpx.AsyncClient(verify=settings.verify_ssl, timeout=None) as client:
            if data:
                # POST request
                response = await client.post(url, headers=headers, json=data)
            else:
                # GET request
                response = await client.get(url, headers=headers)
            
            logging.info(f"Response status: {response.status_code}")

            # If backend returned an error, surface only the helpful detail
            if response.status_code >= 400:
                try:
                    detail = response.json().get("detail", "Unknown error from backend")
                except Exception:
                    detail = response.text or "Unknown error from backend"

                logging.error(f"Backend error ({response.status_code}): {detail}")
                raise Exception(detail)

            # Success path
            return response.json()
    except Exception as e:
        logging.error(f"Request to {url} failed: {e}")
        raise

