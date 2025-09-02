import asyncio
import threading
from pathlib import Path

from fastmcp import FastMCP
import time

from .settings import settings
from .workflow_runner import workflow_runner
from . import co_datascientist_api

mcp = FastMCP("CoDatascientist")


@mcp.tool()
async def optimize_code(code_absolute_path: str, python_absolute_path: str) -> str:
    """
    run this tool to start the workflow to improve python machine learning code, triggered by the user, especially if he asks help from "CoDatascientist".
    the workflow may take a long time, so use the "check_workflow_status" tool continuously to check the workflow status, until the workflow is finished.
    after each "check_workflow_status" call, report the workflow status to the user, and then call "check_workflow_status" again.

    the code improvement process is:
    1. finding evaluation metrics
    2. generating multiple code ideas
    3. running ideas and inspecting results
    4. writing successful ideas to the output folder

    args:
        code_absolute_path: the absolute path to the .py file containing the python machine learning code to be improved.
        python_absolute_path: the absolute path of the python executable. if using the default system interpreter, pass "python" but its recommended to specify the full path.
        args: optional arguments to pass when running the code

    returns:
        status string with cost information
    """
    if workflow_runner.workflow is not None and not workflow_runner.workflow.finished:
        return "Another workflow is already in progress, cannot run more than one simultaneously. Please wait until it finishes, or ask the agent to stop it."

    if not Path(code_absolute_path).exists():
        return "Python code file path doesn't exist."

    code_absolute_path = str(Path(code_absolute_path).resolve())

    if python_absolute_path != "python":
        if not Path(python_absolute_path).exists():
            return "Python interpreter executable path doesn't exist."
        python_absolute_path = str(Path(python_absolute_path).resolve())

    # Check usage status before starting expensive workflow
    try:
        usage_status = await co_datascientist_api.get_user_usage_status()
        usage_msg = f"\n💰 Usage Status: ${usage_status['current_usage_usd']:.2f} / ${usage_status['limit_usd']:.2f} used"
        
        if usage_status['is_blocked']:
            return f"🚨 BLOCKED: Usage limit exceeded! {usage_msg}\nCannot start new workflow. Use 'get_usage_status' tool for details."
        elif usage_status['usage_percentage'] >= 90:
            usage_msg += f" ({usage_status['usage_percentage']:.1f}% - CRITICAL)"
        elif usage_status['usage_percentage'] >= 80:
            usage_msg += f" ({usage_status['usage_percentage']:.1f}% - WARNING)"
        else:
            usage_msg += f" ({usage_status['usage_percentage']:.1f}%)"
    except Exception as e:
        usage_msg = f" (Could not check usage status: {e})"

    print("starting workflow!")
    code = Path(code_absolute_path).read_text()
    project_absolute_path = Path(code_absolute_path).parent

    # create async workflow in new thread. we don't use asyncio.create_task because it interferes with the event loop.
    threading.Thread(
        target=lambda: asyncio.run(workflow_runner.run_workflow(code, python_absolute_path, project_absolute_path)),
        daemon=True  # to make it not block shutdown
    ).start()
    return f"Workflow started successfully!{usage_msg}\n💡 Use 'check_workflow_status' to monitor progress and costs."


@mcp.tool()
async def stop_workflow() -> str:
    """
    schedules stopping the currently running workflow. keep using the "check_workflow_status" tool to check the workflow status until it is finished / stopped.
    """
    if workflow_runner.workflow is None:
        return "No workflow is currently running."
    print("stopping workflow...")
    workflow_runner.should_stop_workflow = True
    return "Workflow scheduled to stop."


@mcp.tool()
async def check_workflow_status() -> dict:
    """
    checks the status of the currently running workflow with real-time cost tracking.
    when the "finished" parameter is True, the workflow is finished. if it finished successfully, suggest the user to replace his code with the improved code as is.
    keep calling this tool, and report the status to the user after each call, until the "finished" parameter is True.

    returns:
        a dictionary with the following keys:
        - status: the current status of the workflow: either "not started" or "finished" or "running idea X out of Y: 'idea_name'"
        - idea: the idea that was used to improve the code.
        - explanation: the explanation for the idea.
        - code: the improved code to be suggested to the user as is.
        - improvement: the improvement metric and result for the idea, compared to the original.
        - duration_seconds: the duration of the workflow in seconds.
        - cost_info: real-time cost and usage information
    """
    print("checking status...")
    time.sleep(settings.wait_time_between_checks_seconds)  # to prevent the agent in cursor from repeatedly asking
    duration_seconds = time.time() - workflow_runner.start_timestamp
    
    # Get cost information
    cost_info = {
        "message": "Cost tracking unavailable",
        "current_usage": "unknown",
        "limit": "unknown",
        "remaining": "unknown"
    }
    
    try:
        if workflow_runner.workflow and workflow_runner.workflow.workflow_id:
            # Get workflow-specific costs
            workflow_costs = await co_datascientist_api.get_workflow_costs(workflow_runner.workflow.workflow_id)
            usage_status = await co_datascientist_api.get_user_usage_status()
            
            cost_info = {
                "message": f"💰 This workflow: ${workflow_costs['cost_usd']:.6f} | Total usage: ${usage_status['current_usage_usd']:.2f} / ${usage_status['limit_usd']:.2f}",
                "workflow_cost": f"${workflow_costs['cost_usd']:.6f}",
                "workflow_tokens": f"{workflow_costs['total_tokens']:,}",
                "current_usage": f"${usage_status['current_usage_usd']:.2f}",
                "limit": f"${usage_status['limit_usd']:.2f}",
                "remaining": f"${usage_status['remaining_usd']:.2f}",
                "usage_percentage": f"{usage_status['usage_percentage']:.1f}%",
                "status_indicator": "🟩" if usage_status['usage_percentage'] < 50 else "🟨" if usage_status['usage_percentage'] < 80 else "🟥"
            }
        else:
            # Get just user totals
            usage_status = await co_datascientist_api.get_user_usage_status()
            cost_info = {
                "message": f"💰 Total usage: ${usage_status['current_usage_usd']:.2f} / ${usage_status['limit_usd']:.2f} ({usage_status['usage_percentage']:.1f}%)",
                "current_usage": f"${usage_status['current_usage_usd']:.2f}",
                "limit": f"${usage_status['limit_usd']:.2f}",
                "remaining": f"${usage_status['remaining_usd']:.2f}",
                "usage_percentage": f"{usage_status['usage_percentage']:.1f}%",
                "status_indicator": "🟩" if usage_status['usage_percentage'] < 50 else "🟨" if usage_status['usage_percentage'] < 80 else "🟥"
            }
    except Exception as e:
        cost_info["message"] = f"💰 Cost tracking error: {str(e)}"
    
    if workflow_runner.workflow is None:
        return {
            "status": "not started",
            "cost_info": cost_info
        }
    if workflow_runner.should_stop_workflow:
        return {
            "status": "scheduled for stopping, waiting for workflow to stop...",
            "cost_info": cost_info
        }
    
    return {
        "status": workflow_runner.workflow.status_text,
        "info": workflow_runner.workflow.info,
        "finished": workflow_runner.workflow.finished,
        "duration_seconds": duration_seconds,
        "cost_info": cost_info
    }


@mcp.tool()
async def get_usage_status() -> dict:
    """
    Get your current usage status and remaining balance. Shows a quick overview similar to 'co-datascientist status' command.
    
    returns:
        dictionary with usage information including:
        - current usage vs limit
        - remaining balance  
        - usage percentage
        - status indicator
        - helpful tips
    """
    try:
        usage_status = await co_datascientist_api.get_user_usage_status()
        
        # Determine status message and emoji
        percentage = usage_status['usage_percentage']
        if usage_status['is_blocked']:
            status_msg = "🚨 BLOCKED - Free tokens exhausted! Contact support or wait for reset."
        elif percentage >= 90:
            status_msg = f"🟥 CRITICAL - Only ${usage_status['remaining_usd']:.2f} remaining!"
        elif percentage >= 80:
            status_msg = f"🟨 WARNING - Approaching limit ({percentage:.1f}% used)"
        elif percentage >= 50:
            status_msg = f"🟦 MODERATE - {percentage:.1f}% of limit used"
        else:
            status_msg = f"🟩 GOOD - Plenty of free tokens remaining"
        
        # Create progress bar representation
        bar_width = 20
        filled = int(bar_width * percentage / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        return {
            "summary": f"💰 Quick Usage Status",
            "used": f"${usage_status['current_usage_usd']:.2f} / ${usage_status['limit_usd']:.2f}",
            "remaining": f"${usage_status['remaining_usd']:.2f}",
            "progress_bar": f"[{bar}] {percentage:.1f}%",
            "status": status_msg,
            "is_blocked": usage_status['is_blocked'],
            "tips": [
                "Use 'get_cost_summary' for basic cost breakdown",
                "Use 'get_detailed_costs' for full analysis",
                "Monitor costs during workflows with 'check_workflow_status'"
            ]
        }
        
    except Exception as e:
        return {
            "error": f"Error getting usage status: {e}",
            "tips": ["Check your network connection", "Verify MCP server is running correctly"]
        }


@mcp.tool()
async def get_cost_summary() -> dict:
    """
    Get a summary of your usage costs and token consumption. Similar to 'co-datascientist costs' command.
    
    returns:
        dictionary with cost summary including:
        - total cost
        - usage limits
        - token counts
        - workflow counts
    """
    try:
        costs_response = await co_datascientist_api.get_user_costs_summary()
        usage_status = await co_datascientist_api.get_user_usage_status()
        
        # Status indicator
        if usage_status['is_blocked']:
            status_indicator = "🚨 BLOCKED - Free tokens exhausted!"
            status_detail = f"You've used ${usage_status['current_usage_usd']:.2f} of your ${usage_status['limit_usd']:.2f} limit."
        elif usage_status['usage_percentage'] >= 80:
            status_indicator = f"⚠️  Approaching limit - {usage_status['usage_percentage']:.1f}% used"
            status_detail = f"${usage_status['remaining_usd']:.2f} remaining"
        else:
            status_indicator = f"✅ Active - {usage_status['usage_percentage']:.1f}% of limit used"
            status_detail = f"${usage_status['remaining_usd']:.2f} remaining"
        
        return {
            "title": "💰 Co-DataScientist Usage Summary",
            "total_cost": f"${costs_response['total_cost_usd']:.8f}",
            "usage_limit": f"${usage_status['limit_usd']:.2f}",
            "remaining": f"${usage_status['remaining_usd']:.2f} ({usage_status['usage_percentage']:.1f}% used)",
            "status": status_indicator,
            "status_detail": status_detail,
            "total_tokens": f"{costs_response['total_tokens']:,}",
            "workflows_completed": costs_response['workflows_completed'],
            "last_updated": costs_response.get('last_updated', 'Unknown'),
            "tip": "💡 Use 'get_detailed_costs' for full breakdown"
        }
        
    except Exception as e:
        return {
            "error": f"Error getting cost summary: {e}",
            "tip": "Check your connection and try again"
        }


@mcp.tool()
async def get_detailed_costs() -> dict:
    """
    Get detailed cost breakdown including all workflows and model calls. Similar to 'co-datascientist costs --detailed' command.
    
    returns:
        dictionary with detailed cost information including:
        - total costs and limits
        - per-workflow breakdown
        - model call details
        - usage status
    """
    try:
        costs_response = await co_datascientist_api.get_user_costs()
        usage_status = await co_datascientist_api.get_user_usage_status()
        
        # Status with emoji
        if usage_status['is_blocked']:
            status_msg = f"🚨 Status: BLOCKED (limit exceeded)"
        elif usage_status['usage_percentage'] >= 80:
            status_msg = f"⚠️  Status: Approaching limit ({usage_status['usage_percentage']:.1f}%)"
        else:
            status_msg = f"✅ Status: Active ({usage_status['usage_percentage']:.1f}% used)"
        
        # Build workflow breakdown
        workflow_breakdown = []
        if costs_response['workflows']:
            for workflow_id, workflow_data in costs_response['workflows'].items():
                workflow_info = {
                    "id": workflow_id[:8] + "...",
                    "cost": f"${workflow_data['cost']:.8f}",
                    "tokens": f"{workflow_data['input_tokens'] + workflow_data['output_tokens']:,}",
                    "model_calls": len(workflow_data['model_calls'])
                }
                
                # Add recent model calls
                recent_calls = []
                for call in workflow_data['model_calls'][-3:]:  # Last 3 calls
                    recent_calls.append({
                        "model": call['model'],
                        "cost": f"${call['cost']:.8f}",
                        "tokens": f"{call['input_tokens']}+{call['output_tokens']}"
                    })
                workflow_info["recent_calls"] = recent_calls
                
                if len(workflow_data['model_calls']) > 3:
                    workflow_info["additional_calls"] = len(workflow_data['model_calls']) - 3
                
                workflow_breakdown.append(workflow_info)
        
        return {
            "title": "💰 Co-DataScientist Usage Details",
            "total_cost": f"${costs_response['total_cost_usd']:.8f}",
            "usage_limit": f"${usage_status['limit_usd']:.2f}",
            "remaining": f"${usage_status['remaining_usd']:.2f}",
            "usage_percentage": f"{usage_status['usage_percentage']:.1f}%",
            "status": status_msg,
            "total_tokens": f"{costs_response['total_tokens']:,} ({costs_response['total_input_tokens']:,} input + {costs_response['total_output_tokens']:,} output)",
            "workflows_count": costs_response['workflows_count'],
            "last_updated": costs_response.get('last_updated', 'Unknown'),
            "workflow_breakdown": workflow_breakdown
        }
        
    except Exception as e:
        return {
            "error": f"Error getting detailed costs: {e}",
            "tip": "Check your connection and try again"
        }


async def run_mcp_server():
    await mcp.run_sse_async(host=settings.host, port=settings.port)
