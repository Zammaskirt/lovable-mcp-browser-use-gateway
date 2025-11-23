#!/usr/bin/env python3
"""Test the agent with a simple task to verify basic functionality."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from agent_runner import run_browser_agent

def test_simple_task():
    """Test with a simple task."""
    print("=" * 60)
    print("TESTING AGENT WITH SIMPLE TASK")
    print("=" * 60)
    
    # Set a shorter timeout for testing
    os.environ['MCP_AGENT_TIMEOUT_SEC'] = '60'  # 60 seconds instead of 600
    
    # Simple task: just navigate to a page
    task = "Navigate to https://example.com and tell me what you see."
    
    print(f"\nTask: {task}")
    print(f"Timeout: {os.environ.get('MCP_AGENT_TIMEOUT_SEC')}s")
    print("\nStarting agent execution...")
    start_time = time.time()
    
    try:
        result = run_browser_agent(task)
        elapsed = time.time() - start_time
        
        print(f"\n{'=' * 60}")
        print("EXECUTION COMPLETED")
        print(f"{'=' * 60}")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Success: {result.get('ok', False)}")
        
        if result.get('ok'):
            print(f"\n[SUCCESS] Task completed successfully!")
            print(f"Result: {result.get('result_text', '')[:500]}")
        else:
            print(f"\n[FAILED] Task failed")
            print(f"Error: {result.get('error', 'No error message')}")
            print(f"Error Code: {result.get('error_code', 'N/A')}")
        
        print(f"\nFull result keys: {list(result.keys())}")
        
        return result.get('ok', False)
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n{'=' * 60}")
        print("EXECUTION FAILED WITH EXCEPTION")
        print(f"{'=' * 60}")
        print(f"Time elapsed: {elapsed:.1f}s")
        print(f"Exception: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_task()
    sys.exit(0 if success else 1)

