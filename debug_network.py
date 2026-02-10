
import os
import sys
import requests
import socket

def check_connectivity(url, description):
    print(f"--- Checking {description}: {url} ---")
    try:
        if "http" not in url:
             # DNS check
             ip = socket.gethostbyname(url)
             print(f"DNS Resolution: {url} -> {ip}")
             return

        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        if response.status_code == 200:
            print("✅ Success")
        else:
            print(f"⚠️ Warning: Non-200 status code")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("=== Network Debugger ===")
    print(f"Environment Variables:")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'TUSHARE_PROXY', 'TUSHARE_HTTP_URL', 'TUSHARE_TOKEN']:
        val = os.getenv(key)
        # Mask token
        if key == 'TUSHARE_TOKEN' and val:
            val = val[:4] + "***" + val[-4:]
        # Highlight whitespace issues with single quotes
        print(f"  {key}: '{val}'")
        
    # 1. Check external internet (Sina)
    # Tushare legacy uses hq.sinajs.cn
    check_connectivity("http://hq.sinajs.cn/list=sh600519", "Sina API (Legacy Data)")

    # 2. Check Custom Tushare URL if set
    custom_url = os.getenv("TUSHARE_HTTP_URL")
    if custom_url:
        check_connectivity(custom_url, "Custom Tushare URL")
    
    # 3. Check official Tushare Website/API
    check_connectivity("http://api.waditu.com", "Official Tushare API Domain")

if __name__ == "__main__":
    main()
