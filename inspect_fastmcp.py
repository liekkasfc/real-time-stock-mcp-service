
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from stock_mcp.app import build_app
from stock_mcp.stock_data_source import WebCrawlerDataSource

try:
    data_source = WebCrawlerDataSource()
    app = build_app(data_source)
    print("FastMCP object attributes:")
    print(dir(app))
    
    print("\nCheck for common ASGI/SSE methods:")
    for attr in ['create_asgi_app', 'mount_asgi_app', 'sse_handler', '_sse_handler', 'run_sse']:
        if hasattr(app, attr):
            print(f"Found: {attr}")
except Exception as e:
    print(e)
