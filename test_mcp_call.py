import requests
import json
import sys
import threading
import time

# Configuration
BASE_URL = "http://192.168.233.50:8001"
SSE_URL = f"{BASE_URL}/sse"
session_endpoint = None

def listen_sse():
    global session_endpoint
    print(f"Connecting to SSE stream at {SSE_URL}...")
    try:
        response = requests.get(SSE_URL, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                if decoded_line.startswith("event: endpoint"):
                    continue
                
                if decoded_line.startswith("data: "):
                    data = decoded_line[6:].strip()
                    if not session_endpoint and "/" in data and "session_id" in data: 
                         session_endpoint = data
                         print(f"Session Endpoint received: {session_endpoint}")
                    else:
                        print(f"Data received: {data}")
                        
    except Exception as e:
        print(f"SSE Error: {e}")

def send_rpc(method, params=None, msg_id=None):
    if not session_endpoint:
        print("Error: No session endpoint")
        return None
        
    full_post_url = f"{BASE_URL}{session_endpoint}"
    payload = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params is not None:
        payload["params"] = params
    if msg_id is not None:
        payload["id"] = msg_id
        
    print(f"Sending {method}: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(full_post_url, json=payload)
        response.raise_for_status()
        print(f"Response Status: {response.status_code}")
        print("Response Body:")
        print(response.text)
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    # Start SSE listener in background thread
    sse_thread = threading.Thread(target=listen_sse)
    sse_thread.daemon = True
    sse_thread.start()
    
    # Wait for session_endpoint
    print("Waiting for session endpoint...")
    for _ in range(10):
        if session_endpoint:
            break
        time.sleep(1)
        
    if not session_endpoint:
        print("Timeout waiting for session endpoint")
        sys.exit(1)

    # 1. Initialize
    init_params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0"
        }
    }
    send_rpc("initialize", init_params, 1)
    
    # Wait a bit for response (though it comes asynchronously via SSE or HTTP response)
    time.sleep(1)
    
    # 2. Initialized notification
    send_rpc("notifications/initialized")
    
    time.sleep(1)
    
    # 3. Call tool
    tool_params = {
        "name": "get_real_time_data",
        "arguments": {
            "symbol": "600105.SH"
        }
    }
    send_rpc("tools/call", tool_params, 2)
    
    # Wait for result
    time.sleep(5)

if __name__ == "__main__":
    main()
