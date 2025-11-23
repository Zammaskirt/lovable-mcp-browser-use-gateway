#!/usr/bin/env python3
"""Test Saik0s CLI with a simpler task."""

import subprocess
import time
import os

def test_saik0s_simple():
    """Test Saik0s CLI with a simple task."""
    
    print("=" * 80)
    print("🧪 SAIK0S CLI - SIMPLE TASK TEST")
    print("=" * 80)
    print()
    
    # Simple task
    task = "Navigate to lovable.dev and take a screenshot"
    
    print(f"📋 Task: {task}")
    print("-" * 80)
    print()
    
    cmd = ["mcp-server-browser-use", "-e", ".env", "run-browser-agent", task]
    env = os.environ.copy()
    timeout = 300  # 5 minutes
    
    print(f"⏳ Running Saik0s CLI with {timeout}s timeout...")
    print()
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        elapsed = time.time() - start
        
        print(f"✅ Completed in {elapsed:.1f}s")
        print()
        print("📋 Output:")
        print("-" * 80)
        print(result.stdout)
        if result.stderr:
            print("📋 Errors:")
            print("-" * 80)
            print(result.stderr)
        
        print()
        print(f"Return code: {result.returncode}")
        
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - start
        print(f"❌ Timed out after {elapsed:.1f}s")
        print()
        print("📋 Output before timeout:")
        print("-" * 80)
        print(e.stdout if e.stdout else "(no stdout)")
        if e.stderr:
            print("📋 Errors:")
            print("-" * 80)
            print(e.stderr)

if __name__ == "__main__":
    test_saik0s_simple()

