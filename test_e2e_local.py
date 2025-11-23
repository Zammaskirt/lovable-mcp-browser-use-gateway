#!/usr/bin/env python3
"""Test the Lovable MCP Gateway locally."""

import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://127.0.0.1:8001"
BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN")
TASK = "Create a basic todo app with add and delete functionality"

print("=" * 80)
print("🧪 LOVABLE MCP GATEWAY - LOCAL E2E TEST")
print("=" * 80)
print()

# Test 1: Health check
print("📋 Test 1: Health Check")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed\n")
except Exception as e:
    print(f"❌ Health check failed: {e}\n")
    exit(1)

# Test 2: Authentication - Missing token
print("📋 Test 2: Authentication - Missing Token")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/tools/run_browser_agent",
        json={"task": "test"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 401
    print("✅ Correctly rejected request without token\n")
except Exception as e:
    print(f"❌ Test failed: {e}\n")

# Test 3: Authentication - Invalid token
print("📋 Test 3: Authentication - Invalid Token")
print("-" * 80)
try:
    response = requests.post(
        f"{BASE_URL}/tools/run_browser_agent",
        json={"task": "test"},
        headers={
            "Authorization": "Bearer invalid-token",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 401
    print("✅ Correctly rejected request with invalid token\n")
except Exception as e:
    print(f"❌ Test failed: {e}\n")

# Test 4: Valid request with proper authentication
print("📋 Test 4: Valid Request with Proper Authentication")
print("-" * 80)
print(f"Task: {TASK}")
print(f"Bearer Token: {BEARER_TOKEN[:20]}...")
print()

start_time = time.time()
print("⏳ Sending request...")

try:
    response = requests.post(
        f"{BASE_URL}/tools/run_browser_agent",
        json={"task": TASK},
        headers={
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        },
        timeout=900  # 15 minutes
    )
    
    elapsed = time.time() - start_time
    print(f"Status: {response.status_code}")
    print(f"Elapsed Time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print()
    
    response_data = response.json()
    print("Response:")
    print(json.dumps(response_data, indent=2))
    print()
    
    if response.status_code == 200:
        print("✅ Request successful!")
        if "preview_url" in response_data:
            print(f"✅ Preview URL: {response_data['preview_url']}")
        if "success" in response_data:
            print(f"✅ Success: {response_data['success']}")
    else:
        print(f"❌ Request failed with status {response.status_code}")
        
except requests.exceptions.Timeout:
    print(f"❌ Request timed out after 900 seconds")
except Exception as e:
    print(f"❌ Request failed: {e}")

print()
print("=" * 80)
print("🧪 TEST COMPLETE")
print("=" * 80)

