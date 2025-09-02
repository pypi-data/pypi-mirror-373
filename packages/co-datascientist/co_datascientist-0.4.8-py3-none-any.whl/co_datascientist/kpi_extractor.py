import re
import json
from typing import Optional
from pathlib import Path


def extract_kpi_from_stdout(stdout: Optional[str]) -> Optional[float]:
    """
    Extract KPI value from stdout text.
    
    Looks for patterns like 'KPI: 0.85' or 'KPI:0.85' in the stdout.
    Returns the first KPI value found as a float, or None if not found.
    
    Args:
        stdout: The stdout text to search in
        
    Returns:
        The KPI value as float, or None if not found
    """
    if not stdout:
        return None
    
    # Primary patterns: 'KPI: 0.85' or 'KPI=0.85'
    patterns = [
        r'KPI\s*[:=]\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)',
        r'KPI\s+([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, stdout, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def extract_kpi_from_result_file(result_file_path: Path) -> Optional[float]:
    """
    Extract KPI value from a result JSON file.
    
    Args:
        result_file_path: Path to the result JSON file
        
    Returns:
        The KPI value as float, or None if not found
    """
    try:
        if not result_file_path.exists():
            return None
            
        with open(result_file_path, 'r') as f:
            result_data = json.load(f)
            
        stdout = result_data.get('stdout')
        return extract_kpi_from_stdout(stdout)
    except (json.JSONDecodeError, IOError):
        return None


def create_kpi_folder_name(original_idea_name: str, kpi_value: Optional[float]) -> str:
    """
    Create folder name with KPI prefix if available.
    
    Args:
        original_idea_name: The original idea name
        kpi_value: The KPI value to prefix with, or None
        
    Returns:
        Folder name in format '{KPI}_{idea_name}' if KPI available, otherwise just idea_name
    """
    if kpi_value is not None:
        # Format KPI to avoid too many decimal places and replace dots with underscores for filesystem safety
        if kpi_value == int(kpi_value):
            kpi_str = str(int(kpi_value))
        else:
            kpi_str = f"{kpi_value:.4f}".rstrip('0').rstrip('.').replace('.', '_')
        return f"{kpi_str}_{original_idea_name}"
    else:
        return original_idea_name


def should_enable_kpi_naming() -> bool:
    """
    Check if KPI-based folder naming should be enabled.
    
    This can be controlled via environment variable or configuration.
    For now, it's always enabled but can be easily disabled.
    
    Returns:
        True if KPI naming should be used, False otherwise
    """
    import os
    return os.getenv('ENABLE_KPI_FOLDER_NAMING', 'true').lower() in ('true', '1', 'yes') 