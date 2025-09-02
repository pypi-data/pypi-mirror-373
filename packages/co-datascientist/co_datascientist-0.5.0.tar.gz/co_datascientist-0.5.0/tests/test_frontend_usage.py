#!/usr/bin/env python3
"""
Test script to verify the frontend usage display functionality.
Run this to test the new usage status and costs commands.
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a CLI command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1

def test_commands():
    """Test the CLI commands"""
    print("🧪 Testing Co-DataScientist Frontend Usage Display")
    print("=" * 50)
    
    # Test basic connection
    print("\n1. Testing basic connection...")
    stdout, stderr, returncode = run_command("cd src && python -m co_datascientist.cli --help")
    if returncode == 0:
        print("✅ CLI is working")
    else:
        print(f"❌ CLI failed: {stderr}")
        return
    
    # Test status command
    print("\n2. Testing status command...")
    stdout, stderr, returncode = run_command("cd src && python -m co_datascientist.cli status")
    print("Status command output:")
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    # Test costs command
    print("\n3. Testing costs command (summary)...")
    stdout, stderr, returncode = run_command("cd src && python -m co_datascientist.cli costs")
    print("Costs command output:")
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    # Test detailed costs command
    print("\n4. Testing costs command (detailed)...")
    stdout, stderr, returncode = run_command("cd src && python -m co_datascientist.cli costs --detailed")
    print("Detailed costs command output:")
    print(stdout)
    if stderr:
        print(f"Errors: {stderr}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\nWhat to look for:")
    print("- Total cost and usage limit should be displayed")
    print("- Remaining money should be shown")
    print("- Usage percentage should be calculated")
    print("- Status indicators (✅🟨🟥🚨) should appear based on usage")
    print("- Progress bar should show in status command")

if __name__ == "__main__":
    # Change to the frontend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    test_commands() 