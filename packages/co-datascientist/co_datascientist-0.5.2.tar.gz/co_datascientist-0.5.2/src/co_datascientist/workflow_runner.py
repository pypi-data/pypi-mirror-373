import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
import asyncio
import pathlib
from pathlib import Path
from datetime import datetime, timezone
import uuid

from .models import Workflow, SystemInfo, CodeResult
from . import co_datascientist_api
from .kpi_extractor import extract_kpi_from_stdout
from .settings import settings

OUTPUT_FOLDER = "co_datascientist_output"
CHECKPOINTS_FOLDER = "co_datascientist_checkpoints"
CURRENT_RUNS_FOLDER = "current_runs"


def print_workflow_info(message: str):
    """Print workflow info with consistent formatting"""
    print(f"   {message}")


def print_workflow_step(message: str):
    """Print workflow step with consistent formatting"""
    print(f"   🔄 {message}")


def print_workflow_success(message: str):
    """Print workflow success with consistent formatting"""
    print(f"   ✅ {message}")


def print_workflow_error(message: str):
    """Print workflow error with consistent formatting"""
    print(f"   ❌ {message}")


class _WorkflowRunner:
    def __init__(self):
        self.workflow: Workflow | None = None
        self.start_timestamp = 0
        self.should_stop_workflow = False
        self.debug_mode = True
        # Track best KPI seen when polling backend
        self._checkpoint_counter: int = 0
        # Track current hypothesis to detect transitions
        self._current_hypothesis: str | None = None

    async def run_workflow(self, code: str, python_path: str, project_absolute_path: str, config: dict, spinner=None, debug: bool = True):
        """Run a complete code evolution workflow.

        - Sequential mode (default): run one code version at a time.
        - Parallel mode: set config['parallel']=N (>1) to run batches of up to N in parallel.
        """
        self.should_stop_workflow = False
        # Set debug mode for the class instance
        self.debug_mode = debug
        
        try:
            if spinner:
                spinner.text = "Waking up the Co-DataScientist"
            self.start_timestamp = time.time()
            self.should_stop_workflow = False 
            self.workflow = Workflow(status_text="Workflow started", user_id="")

            system_info = get_system_info(python_path)
            logging.info(f"user system info: {system_info}")

            if bool(config.get('preflight', True)):
                # Start preflight: engine generates questions
                preflight = await co_datascientist_api.start_preflight(code, system_info)
                self.workflow = preflight.workflow
                # Stop spinner to allow clean input UX
                if spinner:
                    spinner.stop()
                # Print understanding text (from raw LLM output if available), questions, then collect answers
                print("")
                if getattr(preflight, 'raw_text', None):
                    # Derive observation line from raw_text robustly
                    raw = preflight.raw_text.strip()
                    obs_line = None
                    try:
                        for ln in raw.splitlines():
                            s = ln.strip()
                            if not s:
                                continue
                            # Skip numbered question lines like "1. ..."
                            if re.match(r"^\d+\.\s+", s):
                                continue
                            # Prefer a line that starts with a dash or a sentence (not a header)
                            obs_line = s
                            break
                    except Exception:
                        obs_line = None
                    if obs_line:
                        try:
                            # Strip leading dash and label if present
                            obs_line = re.sub(r'^\s*-\s*', '', obs_line)
                            obs_line = re.sub(r'^(positive\s+observation[:\-]\s*)', '', obs_line, flags=re.IGNORECASE)
                        except Exception:
                            pass
                        print(obs_line)
                        print("")
                elif getattr(preflight, 'observation', None):
                    obs = preflight.observation.strip()
                    try:
                        obs = re.sub(r'^\s*-\s*', '', obs)
                        obs = re.sub(r'^(positive\s+observation[:\-]\s*)', '', obs, flags=re.IGNORECASE)
                    except Exception:
                        pass
                    print(obs)
                    print("")
                for idx, q in enumerate(preflight.questions, start=1):
                    q_txt = (q or "").strip()
                    try:
                        # Strip any leading enumeration like "1." to avoid 1. 1. duplication
                        q_txt = re.sub(r'^\s*\d+\.\s*', '', q_txt)
                    except Exception:
                        pass
                    print(f"{idx}. {q_txt}")
                    print("")
                # Now prompt one by one without spinner noise
                answers: list[str] = []
                for idx, q in enumerate(preflight.questions, start=1):
                    ans = input(f"Q{idx}: ").strip()
                    answers.append(ans)
                # Complete preflight: engine summarizes and starts baseline
                response = await co_datascientist_api.complete_preflight(self.workflow.workflow_id, answers)
                self.workflow = response.workflow
            else:
                # Skip preflight entirely for clean backward-compatibility
                response = await co_datascientist_api.start_workflow(code, system_info)
                self.workflow = response.workflow
            if spinner:
                spinner.stop()  # stop spinner without emoji
            print("Lets start exploring your problem space.")
            print("--------------------------------")
            parallel_n = int(config.get('parallel', 1) or 1)
            if parallel_n > 1:
                await self._run_parallel_mode(response, python_path, project_absolute_path, config, spinner, parallel_n)
            else:
                await self._run_sequential_mode(response, python_path, project_absolute_path, config, spinner)

            if self.should_stop_workflow:
                await co_datascientist_api.stop_workflow(self.workflow.workflow_id)
                print_workflow_info("Workflow stopped by user.")
                if spinner:
                    spinner.text = "Workflow stopped"
            else:
                # Check if workflow finished due to baseline failure or successful completion
                ###TODO: if the baseline has cheating then we should tell the user and ignore it here... or maybe just see if the changes themselves INTRODUCE cheating... (not the baseline.)
                if (hasattr(self.workflow, 'baseline_code') and 
                    self.workflow.baseline_code.result is not None and 
                    self.workflow.baseline_code.result.return_code != 0):
                    print_workflow_error("Workflow terminated due to baseline code failure.")
                    print("   📄 Review the error details above and fix your script.")
                    if spinner:
                        spinner.text = "Workflow failed"
                else:
                    print_workflow_success("Workflow completed successfully.")
                    if spinner:
                        spinner.text = "Workflow completed"
        
        except Exception as e:
            if spinner:
                spinner.stop()

            err_msg = str(e)
            # Detect user-facing validation errors coming from backend (prefixed with ❌)
            if err_msg.startswith("❌") and not self.debug_mode:
                # Show concise guidance without stack trace
                print_workflow_error(err_msg)
                return  # Do not re-raise, end gracefully

            # Otherwise, show generic workflow error and re-raise for full trace
            print_workflow_error(f"Workflow error: {err_msg}")
            raise


## Preflight logic moved to backend/engine – no frontend LLM usage

    async def _run_parallel_mode(self, initial_response, python_path: str,
                                 project_absolute_path: str, config: dict,
                                 spinner=None, parallel_n: int = 2):
        """Run workflow in parallel mode using batch endpoints.

        Requests batches of up to parallel_n programs from backend, executes them concurrently,
        sends results back in a single batch, and repeats until finished.
        """
        # Handle baseline from initial response if present
        if initial_response.code_to_run is not None:
            if spinner:
                spinner.stop()
            
            # Run baseline using sequential logic
            if initial_response.code_to_run.name == "baseline":
                if config.get('databricks'):
                    result = _databricks_run_python_code(initial_response.code_to_run.code, python_path, config)
                else:
                    result = _run_python_code(initial_response.code_to_run.code, python_path)
                
                await self._handle_baseline_result(result, initial_response, spinner)
                
                # Submit baseline result
                kpi_value = extract_kpi_from_stdout(result.stdout)
                result.kpi = kpi_value
                code_version = initial_response.code_to_run
                code_version.result = result
                
                try:
                    await self._save_current_run_snapshot(code_version, project_absolute_path, config)
                except Exception as e:
                    logging.warning(f"Failed saving baseline snapshot: {e}")
                
                response = await co_datascientist_api.finished_running_code(
                    self.workflow.workflow_id,
                    code_version,
                    result,
                    kpi_value,
                )
                self.workflow = response.workflow

        if spinner:
            spinner.text = f"Running up to {parallel_n} programs in parallel..."
            spinner.start()

        # Now get batches for hypothesis testing
        batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=parallel_n)

        # If no batch yet, keep polling until we get one or finish
        while (batch_resp.batch_to_run is None
               and not self.workflow.finished
               and not self.should_stop_workflow):
            if spinner:
                spinner.text = "Thinking... (regenerating batch)"
            await asyncio.sleep(1)
            batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=parallel_n)
            self.workflow = batch_resp.workflow

        while (not self.workflow.finished
               and not self.should_stop_workflow):

            if batch_resp.batch_to_run is None:
                if spinner:
                    spinner.text = "Thinking... (regenerating batch)"
                await asyncio.sleep(1)
                batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=parallel_n)
                self.workflow = batch_resp.workflow
                continue

            code_versions = batch_resp.batch_to_run
            batch_id = batch_resp.batch_id

            # Stop spinner to show batch hypotheses
            if spinner:
                spinner.stop()

            # Print all hypotheses in the batch (matching sequential mode format) - only for first attempts
            first_attempts = [cv for cv in code_versions if cv.retry_count == 0]
            
            # Check for hypothesis transitions in parallel mode
            for cv in first_attempts:
                if (self._current_hypothesis is not None and 
                    self._current_hypothesis != cv.hypothesis):
                    # Previous hypothesis failed - show failure message
                    print()
                    print(" - Failed implementation - moving on to other hypotheses")
                    print("--------------------------------")
                    break
            
            if first_attempts:  # Only print separator if we have new hypotheses (not retries)
                print("--------------------------------")
            for cv in first_attempts:
                # All items in batch should be hypotheses (baseline handled separately)
                print(f"Testing hypothesis: {cv.hypothesis or 'Unknown hypothesis'}")
                # Track this hypothesis
                self._current_hypothesis = cv.hypothesis

            # Restart spinner for execution
            if spinner:
                spinner.text = f"Running {len(code_versions)} programs in parallel..."
                spinner.start()

            # Execute all code versions concurrently (CPU-bound/blocking -> run in threads)
            def _execute(cv):
                if config.get('databricks'):
                    return _databricks_run_python_code(cv.code, python_path, config)
                else:
                    return _run_python_code(cv.code, python_path)

            tasks = [asyncio.to_thread(_execute, cv) for cv in code_versions]
            results: list[CodeResult] = await asyncio.gather(*tasks, return_exceptions=False)

            # Stop spinner to show results
            if spinner:
                spinner.stop()

            # Attach KPI values and prepare payload tuples
            tuples: list[tuple[str, CodeResult]] = []
            for cv, res in zip(code_versions, results):
                kpi_value = extract_kpi_from_stdout(res.stdout)
                res.kpi = kpi_value
                tuples.append((cv.code_version_id, res))

            # Get baseline KPI for comparison (baseline already handled separately)
            baseline_kpi = None
            if self.workflow.baseline_code and self.workflow.baseline_code.result:
                baseline_kpi = extract_kpi_from_stdout(self.workflow.baseline_code.result.stdout)
            

            # Print results for each hypothesis (matching sequential mode format) - only when KPI is valid
            for cv, res in zip(code_versions, results):
                kpi_value = extract_kpi_from_stdout(res.stdout)
                # Only show hypothesis results if we have a valid KPI and successful execution
                if kpi_value is not None and res.return_code == 0:
                    # Calculate hypothesis outcome if we have baseline for comparison
                    # Clear current hypothesis since it succeeded
                    self._current_hypothesis = None
                    if baseline_kpi is not None:
                        hypothesis_outcome = True if baseline_kpi < kpi_value else False
                        print()
                        print(f" - Hypothesis: {hypothesis_outcome}, KPI: {kpi_value}")
                    else:
                        # Fallback when baseline comparison not available
                        print()
                        print(f" - Hypothesis: KPI = {kpi_value}")
                elif cv.hypothesis_outcome == "failed":
                    # Backend marked this hypothesis as failed after exhausting retries
                    self._current_hypothesis = None
                    print()
                    print(" - Failed implementation - moving on to other hypotheses")
                # Skip showing anything for ongoing retry attempts
            
            if code_versions:  # Only print separator if we had hypotheses
                print("--------------------------------")

            # Save a simple snapshot of the most recently processed run in this batch
            try:
                if code_versions and results:
                    last_cv = code_versions[-1]
                    last_cv.result = results[-1]
                    await self._save_current_run_snapshot(last_cv, project_absolute_path, config)
            except Exception as e:
                logging.warning(f"Failed saving current run snapshot (parallel): {e}")

            # Submit batch results and get next batch
            batch_resp = await co_datascientist_api.finished_running_batch(
                self.workflow.workflow_id,
                batch_id,
                tuples,
            )
            # Update workflow state
            self.workflow = batch_resp.workflow

            # Optionally display live best KPI (only for meaningful attempts, not retries)
            has_meaningful_results = any(cv.retry_count == 0 or cv.hypothesis_outcome in ["supported", "refuted", "failed"] 
                                       for cv in code_versions)
            if has_meaningful_results:
                try:
                    best_info = await co_datascientist_api.get_workflow_population_best(self.workflow.workflow_id)
                    best_kpi = best_info.get("best_kpi") if best_info else None
                    if best_kpi is not None and spinner:
                        spinner.write(f"Current best KPI: {best_kpi}")
                    # Save checkpoint snapshot of current best (parity with sequential mode)
                    best_cv = best_info.get("best_code_version") if best_info else None
                    if best_cv and best_kpi is not None:
                        await self._save_population_best_checkpoint(best_cv, best_kpi, project_absolute_path, config)

                    elif best_kpi is not None and spinner:
                        spinner.write(f"⚠️  No code version available for checkpoint (KPI: {best_kpi})")
                except Exception:
                    pass

    async def _run_sequential_mode(self, response, python_path: str, 
                                  project_absolute_path: str, config: dict, spinner=None, poll_interval: int = 1):
        """Run workflow in sequential mode"""
        
        iteration_count = 0

        while not self.workflow.finished and response.code_to_run is not None and not self.should_stop_workflow:

            # Check for hypothesis transition (previous one failed if we're starting a new one)
            if (response.code_to_run.name != "baseline" and 
                response.code_to_run.retry_count == 0 and 
                self._current_hypothesis is not None and 
                self._current_hypothesis != response.code_to_run.hypothesis):
                # Previous hypothesis failed - show failure message
                print()
                print(" - Failed implementation - moving on to other hypotheses")
                print("--------------------------------")
            
            # Only show "Testing hypothesis" message on first attempt (not during debugging retries)
            if response.code_to_run.name != "baseline" and response.code_to_run.retry_count == 0:
                print("--------------------------------")
                print(f"Testing hypothesis: {response.code_to_run.hypothesis}")
                # Track this hypothesis
                self._current_hypothesis = response.code_to_run.hypothesis
                if spinner:
                    spinner.text = "Testing hypothesis"
                    spinner.start()
            elif response.code_to_run.name != "baseline" and response.code_to_run.retry_count > 0:
                # During retry attempts, just update spinner text without printing
                if spinner:
                    spinner.text = f"Debugging attempt {response.code_to_run.retry_count}"
                    spinner.start()
            # Section where we run the code with particulal cloud integration.
            if config.get('databricks'):
                result = _databricks_run_python_code(response.code_to_run.code, python_path, config)
            else:
                result = _run_python_code(response.code_to_run.code, python_path)

            # Log only for baseline; skip verbose output for other ideas
            if response.code_to_run.name == "baseline":
                await self._handle_baseline_result(result, response, spinner)
                baseline_kpi_value = extract_kpi_from_stdout(result.stdout)

            if spinner:
                spinner.stop() # Stop the testing hypothesis spinner.

            # Prepare objects for backend
            kpi_value = extract_kpi_from_stdout(result.stdout)
            result.kpi = kpi_value
            code_version = response.code_to_run
            code_version.result = result
            try:
                hypothesis_outcome = True if baseline_kpi_value < kpi_value else False ### Sometimes the KPI is none coming out..
            except Exception as e:
                hypothesis_outcome = False

            # Handle different outcomes for non-baseline code
            if response.code_to_run.name != "baseline":
                if kpi_value is not None and result.return_code == 0:
                    # Successful execution with valid KPI - clear current hypothesis
                    self._current_hypothesis = None
                    print()
                    print(f" - Hypothesis: {hypothesis_outcome}, KPI: {kpi_value}")
                    print("--------------------------------")
                # For failures, we'll check the hypothesis_outcome after backend processing

            # Save a simple snapshot of the most recent run
            try:
                await self._save_current_run_snapshot(code_version, project_absolute_path, config)
            except Exception as e:
                logging.warning(f"Failed saving current run snapshot: {e}")

            if spinner:
                spinner.text = "Generating new hypothesis"
                spinner.start()

            response = await co_datascientist_api.finished_running_code(
                self.workflow.workflow_id,
                code_version,
                result,
                kpi_value,
            )
            self.workflow = response.workflow
            
            # Check if backend marked this hypothesis as failed (after exhausting retries)
            if (response.code_to_run and 
                response.code_to_run.name != "baseline" and 
                response.code_to_run.hypothesis_outcome == "failed"):
                # Clear current hypothesis since it failed
                self._current_hypothesis = None
                print()
                print(" - Failed implementation - moving on to other hypotheses")
                print("--------------------------------")

            # Keep polling for next candidate if none returned yet
            while (not self.workflow.finished
                   and response.code_to_run is None
                   and not self.should_stop_workflow):
                if spinner:
                    spinner.text = "Generating new hypothesis"
                batch_resp = await co_datascientist_api.get_batch_to_run(self.workflow.workflow_id, batch_size=1)
                self.workflow = batch_resp.workflow
                if batch_resp.batch_to_run:
                    response.code_to_run = batch_resp.batch_to_run[0]
                    break
                await asyncio.sleep(1)

            # Poll backend for best KPI every poll_interval iterations
            # But skip during retry debugging attempts
            iteration_count += 1
            
            # Skip best KPI logging if this is a retry attempt
            is_retry_attempt = (response.code_to_run and 
                              response.code_to_run.name != "baseline" and 
                              response.code_to_run.retry_count > 0)
            
            should_show_best_kpi = (iteration_count % poll_interval == 0 and not is_retry_attempt)
            
            if should_show_best_kpi:
                try:
                    best_info = await co_datascientist_api.get_workflow_population_best(self.workflow.workflow_id)
                    best_kpi = best_info.get("best_kpi") if best_info else None
                    if best_kpi is not None and spinner:
                        spinner.write(f"Current best KPI: {best_kpi}")

                    # Always save checkpoint snapshot of current best
                    best_cv = best_info.get("best_code_version") if best_info else None
                    if best_cv and best_kpi is not None:
                        await self._save_population_best_checkpoint(best_cv, best_kpi, project_absolute_path, config)
                    elif best_kpi is not None:
                        if spinner:
                            spinner.write(f"⚠️  No code version available for checkpoint (KPI: {best_kpi})")
                except Exception as e:
                    # Non-fatal: just log and continue
                    logging.warning(f"Failed fetching best KPI code: {e}")

    async def _handle_baseline_result(self, result: CodeResult, response, spinner=None):
        """Handle result in standard mode (original behavior)"""
        # Check if code execution failed and provide clear feedback
        if result.return_code != 0:
            # Code failed - show error details
            print_workflow_error(f"'{response.code_to_run.name}' failed with exit code {result.return_code}")
            if result.stderr:
                print("   📄 Error details:")
                # Print each line of stderr with proper indentation
                for line in result.stderr.strip().split('\n'):
                    if spinner:
                        spinner.write(f"      {line}")
                    else:
                        print(f"      {line}")
            
            # For baseline failures, give specific guidance
            if response.code_to_run.name == "baseline":
                print("   💡 The baseline code failed to run. This will stop the workflow.")
                print("   💡 Check the error above and fix your script before running again.")
                if "ModuleNotFoundError" in (result.stderr or ""):
                    print("   💡 Missing dependencies? Try: pip install <missing-package>")
        else:
            # Code succeeded - show success message
            kpi_value = extract_kpi_from_stdout(result.stdout)
            if kpi_value is not None:
                msg = f"Completed '{response.code_to_run.name}' | KPI = {kpi_value}"
                if spinner:
                    spinner.write(msg)
                    print("--------------------------------")
                else:
                    print_workflow_success(msg)
            else:
                msg = f"Completed '{response.code_to_run.name}'"
                if spinner:
                    spinner.write(msg)
                else:
                    print_workflow_success(msg)

    async def _save_population_best_checkpoint(self, best_cv, best_kpi: float, project_absolute_path: str, config: dict):
        """Persist best code/KPI - to Databricks volume if using Databricks, locally otherwise."""
        try:
            if not best_cv or best_kpi is None:
                return

            # Convert best_cv to CodeVersion model if it is raw dict
            from .models import CodeVersion, CodeResult
            if isinstance(best_cv, dict):
                try:
                    # Nested result may also be dict – handle gracefully
                    if isinstance(best_cv.get("result"), dict):
                        # Ensure runtime_ms field may be missing; allow extra
                        best_cv["result"] = CodeResult.model_validate(best_cv["result"])  # type: ignore
                    best_cv = CodeVersion.model_validate(best_cv)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse best_code_version payload: {e}")
                    return

            safe_name = _make_filesystem_safe(best_cv.name or "best")
            base_filename = f"best_{self._checkpoint_counter}_{safe_name}"

            # Prepare metadata
            meta = {
                "code_version_id": best_cv.code_version_id,
                "name": best_cv.name,
                "kpi": best_kpi,
                "stdout": getattr(best_cv.result, "stdout", None) if best_cv.result else None,
            }

            # Check if using Databricks
            is_databricks = config and config.get('databricks')
            if is_databricks:
                # Save directly to Databricks volume using CLI (no local storage)
                await self._save_checkpoint_to_databricks_volume(
                    best_cv.code, 
                    json.dumps(meta, indent=4), 
                    base_filename, 
                    config
                )
            else:
                # Original behavior for local runs
                checkpoints_base = Path(project_absolute_path) / CHECKPOINTS_FOLDER
                checkpoints_base.mkdir(parents=True, exist_ok=True)
                
                code_path = checkpoints_base / f"{base_filename}.py"
                meta_path = checkpoints_base / f"{base_filename}.json"
                
                code_path.write_text(best_cv.code, encoding="utf-8")
                meta_path.write_text(json.dumps(meta, indent=4))

            self._checkpoint_counter += 1
        except Exception as e:
            logging.warning(f"Failed saving best checkpoint: {e}")

    async def _save_checkpoint_to_databricks_volume(self, code_content: str, meta_content: str, base_filename: str, config: dict):
        """Save checkpoint files directly to Databricks volume using CLI (following existing upload pattern)."""
        try:
            # Extract databricks configuration (same pattern as _databricks_run_python_code)
            if isinstance(config['databricks'], dict):
                databricks_config = config['databricks']
            else:
                databricks_config = config
            
            CLI = databricks_config.get('cli', "databricks")
            VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")
            
            # Ensure checkpoints directory exists
            checkpoints_dir = f"{VOLUME_URI}/{CHECKPOINTS_FOLDER}"
            mkdir_result = subprocess.run([CLI, "fs", "mkdir", checkpoints_dir], 
                                        capture_output=True, text=True)
            # mkdir is okay to fail if directory already exists
            
            # Create remote paths
            remote_code_path = f"{checkpoints_dir}/{base_filename}.py"
            remote_meta_path = f"{checkpoints_dir}/{base_filename}.json"
            
            # Save code file using temp file + CLI upload pattern (following existing code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code = pathlib.Path(f.name)
            
            # Try uploading code file
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
                           "--overwrite", "--output", "json"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to upload checkpoint code: {result.stderr}")
                return
            os.unlink(local_tmp_code)
            
            # Save metadata file using temp file + CLI upload pattern
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta = pathlib.Path(f.name)
            
            # Try uploading metadata file
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
                           "--overwrite", "--output", "json"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to upload checkpoint metadata: {result.stderr}")
                return
            os.unlink(local_tmp_meta)
            
            # print(f"✅ Checkpoint uploaded to: {VOLUME_URI}/{CHECKPOINTS_FOLDER}/{base_filename}.*")
            
        except Exception as e:
            print(f"❌ Checkpoint upload error: {e}")

    async def _save_current_run_to_databricks_volume(self, code_content: str, meta_content: str, config: dict, unique_id: str, timestamp: str):
        """Save current run files directly to Databricks volume under `current_runs` directory."""
        try:
            if isinstance(config['databricks'], dict):
                databricks_config = config['databricks']
            else:
                databricks_config = config

            CLI = databricks_config.get('cli', "databricks")
            VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")

            # Ensure current_runs directory exists
            current_dir = f"{VOLUME_URI}/{CURRENT_RUNS_FOLDER}"
            subprocess.run([CLI, "fs", "mkdir", current_dir], capture_output=True, text=True)

            remote_code_path = f"{current_dir}/latest.py"
            remote_meta_path = f"{current_dir}/latest.json"
            uid_safe = _make_filesystem_safe(unique_id)
            ts_safe = _make_filesystem_safe(timestamp)
            remote_code_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.py"
            remote_meta_uid_path = f"{current_dir}/run_{ts_safe}_{uid_safe}.json"

            # Upload code
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code), remote_code_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_code)
            if result.returncode != 0:
                print(f"❌ Failed to upload current run code: {result.stderr}")
                return

            # Upload code (UUID version)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code_content.encode())
                local_tmp_code_uid = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_code_uid), remote_code_uid_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_code_uid)
            if result.returncode != 0:
                print(f"❌ Failed to upload current run code (uuid): {result.stderr}")
                return

            # Upload metadata
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta), remote_meta_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_meta)
            if result.returncode != 0:
                print(f"❌ Failed to upload current run metadata: {result.stderr}")
                return

            # Upload metadata (UUID version)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
                f.write(meta_content.encode())
                local_tmp_meta_uid = pathlib.Path(f.name)
            result = subprocess.run([CLI, "fs", "cp", str(local_tmp_meta_uid), remote_meta_uid_path,
                                     "--overwrite", "--output", "json"], capture_output=True, text=True)
            os.unlink(local_tmp_meta_uid)
            if result.returncode != 0:
                print(f"❌ Failed to upload current run metadata (uuid): {result.stderr}")
                return

            # print(f"✅ Current run uploaded to: {VOLUME_URI}/{CURRENT_RUNS_FOLDER}/latest.* and run_{uid_safe}.*")
        except Exception as e:
            print(f"❌ Current run upload error: {e}")

    async def _save_current_run_snapshot(self, code_version, project_absolute_path: str, config: dict):
        """Persist the most recent run (code + minimal meta) to `current_runs`.

        Keeps it simple: always overwrite `latest.py` and `latest.json`.
        Mirrors Databricks behavior if configured.
        """
        try:
            if not code_version:
                return

            from .models import CodeVersion, CodeResult
            if isinstance(code_version, dict):
                try:
                    if isinstance(code_version.get("result"), dict):
                        code_version["result"] = CodeResult.model_validate(code_version["result"])  # type: ignore
                    code_version = CodeVersion.model_validate(code_version)  # type: ignore
                except Exception as e:
                    logging.warning(f"Cannot parse code_version payload for current run: {e}")
                    return

            meta = {
                "code_version_id": code_version.code_version_id,
                "name": code_version.name,
                "kpi": getattr(code_version.result, "kpi", None) if code_version.result else None,
                "stdout": getattr(code_version.result, "stdout", None) if code_version.result else None,
            }

            is_databricks = config and config.get('databricks')
            unique_id = getattr(code_version, 'code_version_id', None) or str(uuid.uuid4())
            uid_safe = _make_filesystem_safe(unique_id)
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            ts_safe = _make_filesystem_safe(timestamp)
            if is_databricks:
                await self._save_current_run_to_databricks_volume(
                    code_version.code,
                    json.dumps(meta, indent=4),
                    config,
                    unique_id,
                    timestamp
                )
            else:
                current_runs_base = Path(project_absolute_path) / CURRENT_RUNS_FOLDER
                current_runs_base.mkdir(parents=True, exist_ok=True)

                code_path = current_runs_base / "latest.py"
                meta_path = current_runs_base / "latest.json"
                code_uid_path = current_runs_base / f"run_{ts_safe}_{uid_safe}.py"
                meta_uid_path = current_runs_base / f"run_{ts_safe}_{uid_safe}.json"

                code_path.write_text(code_version.code, encoding="utf-8")
                meta_path.write_text(json.dumps(meta, indent=4))
                code_uid_path.write_text(code_version.code, encoding="utf-8")
                meta_uid_path.write_text(json.dumps(meta, indent=4))
        except Exception as e:
            logging.warning(f"Failed saving current run: {e}")


def _make_filesystem_safe(name):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", '_', name)


def _run_python_code(code: str, python_path: str) -> CodeResult:
    import subprocess  # Ensure subprocess is imported
    start_time = time.time()
    # write the code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name

    command = [python_path, temp_file_path]

    # run the command
    logging.info("running command: " + str(command))
    try:
        output = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                input="",  # prevents it from blocking on stdin
                                timeout=settings.script_execution_timeout)  # Use centralized timeout
        return_code = output.returncode
        out = output.stdout
        err = output.stderr
    except subprocess.TimeoutExpired as e:
        # Handle timeout gracefully - mark as failed case and continue
        return_code = -9  # Standard timeout return code
        out = None
        err = f"Process timed out after {settings.script_execution_timeout} seconds"
        logging.info(f"Process timed out after {settings.script_execution_timeout} seconds")
    
    if isinstance(out, str) and out.strip() == "":
        out = None
    if isinstance(err, str) and err.strip() == "":
        err = None

    logging.info("stdout: " + str(out))
    logging.info("stderr: " + str(err))

    # delete the temporary file
    os.remove(temp_file_path)
    runtime_ms = int((time.time() - start_time) * 1000)
    return CodeResult(stdout=out, stderr=err, return_code=return_code, runtime_ms=runtime_ms)


def _databricks_run_python_code(code: str,
                                python_path: str = "python", 
                                config: dict = None) -> CodeResult:
    """
    Execute `code` on Databricks Serverless Jobs and collect stdout/err.
    
    Args:
        code: Python code to execute
        python_path: Python path (accepted for API parity, currently ignored)
        config: Configuration dict containing databricks settings. Supports two formats:
                Format 1 (nested): databricks: {cli: "databricks", volume_uri: "...", job: {...}}
                Format 2 (flat): databricks: true, cli: "databricks", volume_uri: "...", job: {...}
                Settings:
                - cli: Databricks CLI command (default: "databricks")
                - volume_uri: DBFS volume URI (default: "dbfs:/Volumes/workspace/default/volume")
                - code_path: Specific DBFS path for code file (optional, overrides volume_uri)
                - timeout: Job timeout (default: "30m")
                - job: Job configuration with name, tasks, environments
    
    Returns:
        CodeResult with stdout, stderr, return_code, and runtime_ms
    """
    # Extract databricks configuration with sensible defaults
    # Support both nested structure (databricks: {config}) and flat structure (databricks: true + top-level config)
    if config and config.get('databricks'):
        if isinstance(config['databricks'], dict):
            # New nested structure: databricks: {cli: ..., volume_uri: ..., etc}
            databricks_config = config['databricks']
            job_config = databricks_config.get('job', {})
        else:
            # Original flat structure: databricks: true + top-level fields
            databricks_config = config
            job_config = config.get('job', {})
    else:
        databricks_config = {}
        job_config = {}
    
    CLI = databricks_config.get('cli', "databricks")
    VOLUME_URI = databricks_config.get('volume_uri', "dbfs:/Volumes/workspace/default/volume")
    CODE_PATH = databricks_config.get('code_path', None)  # Specific code path if provided
    TIMEOUT = databricks_config.get('timeout', "30m")
    logging.info(f"CLI: {CLI}")
    logging.info(f"VOLUME_URI: {VOLUME_URI}")
    logging.info(f"CODE_PATH: {CODE_PATH}")
    logging.info(f"TIMEOUT: {TIMEOUT}")
    t0 = time.time()

    # ------------------------------------------------------------------ 1. write & upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        local_tmp = pathlib.Path(f.name)

    # Always use temp filename to avoid overwriting original code_path
    # The code_path is only for reading the original script, never for writing iterations
    remote_uri = f"{VOLUME_URI}/{local_tmp.name}"
    subprocess.run([CLI, "fs", "cp", str(local_tmp), remote_uri,
                    "--overwrite", "--output", "json"], check=True)  # :contentReference[oaicite:7]{index=7}
    os.unlink(local_tmp) #does this delete the local temp file? 

    # ------------------------------------------------------------------ 2. build job JSON
    # job_config is already extracted above based on config structure
    
    # Build job name with template substitution
    job_name_template = job_config.get('name', 'run-<script-stem>-<timestamp>')
    job_name = job_name_template.replace('<script-stem>', local_tmp.stem).replace('<timestamp>', str(int(t0)))
    
    # Build tasks configuration
    default_task = {
        "task_key": "t",
        "spark_python_task": {"python_file": remote_uri},
        "environment_key": "default"
    }
    tasks = job_config.get('tasks', [default_task])
    # Update the python_file path in the first task
    if tasks and 'spark_python_task' in tasks[0]:
        tasks[0]['spark_python_task']['python_file'] = remote_uri
    
    # Build environments configuration
    default_environments = [{
        "environment_key": "default",
        "spec": {"client": "1"}
    }]
    environments = job_config.get('environments', default_environments)
    
    job_json = {
        "name": job_name,
        "tasks": tasks,
        "environments": environments
    }
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as spec:
        json.dump(job_json, spec)
        spec_path = spec.name

    # ------------------------------------------------------------------ 3. create job
    create = subprocess.run([CLI, "jobs", "create",
                             "--json", f"@{spec_path}", "--output", "json"],
                            text=True, capture_output=True, check=True)
    job_id = json.loads(create.stdout)["job_id"]          # :contentReference[oaicite:9]{index=9}
    
    # Clean up the job spec file
    os.unlink(spec_path)

    # ------------------------------------------------------------------ 4. run job (blocks)
    try:
        output = subprocess.run([CLI, "jobs", "run-now",
                                str(job_id),
                                "--timeout", TIMEOUT,
                                "--output", "json"],
                                text=True, input="", capture_output=True)
        
        # Check if job submission failed
        if output.returncode != 0 or not output.stdout.strip():
            # Job submission failed - return error result
            runtime_ms = int((time.time() - t0) * 1000)
            error_msg = "Databricks job submission failed"
            if output.stderr:
                error_msg += f": {output.stderr}"
            elif not output.stdout.strip():
                error_msg += ": Empty response from Databricks"
            
            logging.error(f"Job submission failed: stdout='{output.stdout}', stderr='{output.stderr}', returncode={output.returncode}")
            return CodeResult(stdout=None, stderr=error_msg, return_code=1, runtime_ms=runtime_ms)
        
        # Parse the job run response
        try:
            run_response = json.loads(output.stdout)
            run_id = run_response["run_id"]
        except (json.JSONDecodeError, KeyError) as e:
            runtime_ms = int((time.time() - t0) * 1000)
            logging.error(f"Failed to parse job run response: {e}, stdout='{output.stdout}'")
            return CodeResult(stdout=None, stderr=f"Failed to parse Databricks response: {e}", 
                            return_code=1, runtime_ms=runtime_ms)

    except subprocess.TimeoutExpired:
        # Handle timeout gracefully - mark as failed case and continue
        runtime_ms = int((time.time() - t0) * 1000)
        error_msg = f"Databricks job submission timed out after {TIMEOUT}"
        logging.info(error_msg)
        return CodeResult(stdout=None, stderr=error_msg, return_code=-9, runtime_ms=runtime_ms)

    # ------------------------------------------------------------------ 5. find child task-run
    try:
        get_run = subprocess.run([CLI, "jobs", "get-run", str(run_id),
                                  "--output", "json"],
                                 text=True, capture_output=True, check=True)
        task_run_id = json.loads(get_run.stdout)["tasks"][0]["run_id"]

        # ------------------------------------------------------------------ 6. fetch logs
        out_json = subprocess.run([CLI, "jobs", "get-run-output",
                                   str(task_run_id), "--output", "json"],
                                  text=True, capture_output=True, check=True)
        out = json.loads(out_json.stdout)
        logs = out.get("logs")
        result_state = out.get("metadata", {}).get("state", {}).get("result_state", "FAILED")

        rc = 0 if result_state == "SUCCESS" else 1
        runtime_ms = int((time.time() - t0) * 1000)

        # Extract error details if available
        stderr_msg = None if rc == 0 else "Task failed"
        if rc != 0 and out.get("error"):
            stderr_msg = f"Task failed: {out['error']}"

        return CodeResult(stdout=logs, stderr=stderr_msg, return_code=rc, runtime_ms=runtime_ms)
        
    except Exception as e:
        # Handle any errors in fetching run details/logs
        runtime_ms = int((time.time() - t0) * 1000)
        logging.error(f"Failed to fetch Databricks job results: {e}")
        return CodeResult(stdout=None, stderr=f"Failed to fetch job results: {e}", 
                        return_code=1, runtime_ms=runtime_ms)




def get_system_info(python_path: str) -> SystemInfo:
    return SystemInfo(
        python_libraries=_get_python_libraries(python_path),
        python_version=_get_python_version(python_path),
        os=sys.platform
    )


def _get_python_libraries(python_path: str) -> list[str]:
    try:
        # Use importlib.metadata to get installed packages (works in all Python 3.8+ environments)
        python_code = """
import importlib.metadata
for dist in importlib.metadata.distributions():
    print(f"{dist.metadata['Name']}=={dist.version}")
"""
        installed_libraries = subprocess.check_output(
            [python_path, "-c", python_code],
            universal_newlines=True
        ).strip()
        return [lib.strip() for lib in installed_libraries.split("\n") if lib.strip()]
    except subprocess.CalledProcessError:
        # If that fails, return empty list
        return []


def _get_python_version(python_path: str) -> str:
    return subprocess.check_output(
        [python_path, "--version"],
        universal_newlines=True
    ).strip()


workflow_runner = _WorkflowRunner()

    
    
