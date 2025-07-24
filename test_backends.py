#!/usr/bin/env python3
"""
Test script for both Flask and Node.js backends
Tests basic functionality and MongoDB integration
"""

import requests
import json
import time
from datetime import datetime

# Backend configurations
FLASK_BASE_URL = "http://localhost:5000"
NODEJS_BASE_URL = "http://localhost:3000"

def test_backend(base_url, backend_name):
    """Test a backend's basic functionality"""
    print(f"\n=== Testing {backend_name} Backend ({base_url}) ===")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Status: {response.json()}")
        else:
            print("✗ Health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {backend_name} backend")
        return False
    
    # Test SIM card registration
    sim_data = {
        "sim_id": f"TEST_SIM_{int(time.time())}",
        "phone_number": "+1234567890",
        "carrier": "Test Carrier"
    }
    
    try:
        response = requests.post(f"{base_url}/api/sim-cards", json=sim_data)
        if response.status_code == 201:
            print("✓ SIM card registration passed")
        else:
            print(f"✗ SIM card registration failed: {response.text}")
    except Exception as e:
        print(f"✗ SIM card registration error: {e}")
    
    # Test message creation
    message_data = {
        "sim_id": sim_data["sim_id"],
        "type": "sms",
        "from": "+1234567890",
        "to": "+0987654321",
        "message": f"Test message from {backend_name} at {datetime.now()}"
    }
    
    try:
        response = requests.post(f"{base_url}/api/messages", json=message_data)
        if response.status_code == 201:
            print("✓ Message creation passed")
            message_id = response.json().get('message_id')
            
            # Test message retrieval
            response = requests.get(f"{base_url}/api/messages?sim_id={sim_data['sim_id']}")
            if response.status_code == 200:
                messages = response.json().get('messages', [])
                if messages:
                    print("✓ Message retrieval passed")
                    print(f"  Retrieved {len(messages)} message(s)")
                else:
                    print("✗ No messages retrieved")
            
            # Test message processing (if message_id is available)
            if message_id:
                response = requests.put(f"{base_url}/api/messages/{message_id}/processed")
                if response.status_code == 200:
                    print("✓ Message processing passed")
                else:
                    print("✗ Message processing failed")
                    
        else:
            print(f"✗ Message creation failed: {response.text}")
    except Exception as e:
        print(f"✗ Message creation error: {e}")
    
    # Test SIM cards retrieval
    try:
        response = requests.get(f"{base_url}/api/sim-cards")
        if response.status_code == 200:
            sim_cards = response.json().get('sim_cards', [])
            print(f"✓ SIM cards retrieval passed ({len(sim_cards)} cards)")
        else:
            print("✗ SIM cards retrieval failed")
    except Exception as e:
        print(f"✗ SIM cards retrieval error: {e}")
    
    # Test SimakoHost endpoints
    try:
        response = requests.get(f"{base_url}/api/simakohost/status")
        if response.status_code == 200:
            print("✓ SimakoHost status endpoint passed")
        else:
            print("✗ SimakoHost status endpoint failed")
    except Exception as e:
        print(f"✗ SimakoHost status endpoint error: {e}")
    
    return True

def main():
    """Main test function"""
    print("Simako Backend Test Suite")
    print("=" * 50)
    
    # Test both backends
    flask_ok = test_backend(FLASK_BASE_URL, "Flask")
    nodejs_ok = test_backend(NODEJS_BASE_URL, "Node.js")
    
    print(f"\n=== Test Summary ===")
    print(f"Flask Backend: {'✓ PASSED' if flask_ok else '✗ FAILED'}")
    print(f"Node.js Backend: {'✓ PASSED' if nodejs_ok else '✗ FAILED'}")
    
    if flask_ok and nodejs_ok:
        print("\n🎉 All tests passed! Both backends are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\nMake sure:")
        print("- MongoDB is running")
        print("- Both backends are started")
        print("- No firewall issues")

if __name__ == "__main__":
    main()
