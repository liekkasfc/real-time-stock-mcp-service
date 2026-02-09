"""
股票数据 MCP Server（SSE 入口）
"""
import logging
import os
import signal
import sys
from stock_mcp.app import build_app
from stock_mcp.stock_data_source import WebCrawlerDataSource
from stock_mcp.utils.utils import setup_logging

def main():
    """
    Run the MCP server with SSE transport.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    setup_logging(level=getattr(logging, log_level, logging.INFO))
    logger = logging.getLogger(__name__)

    # 1) Dependency Injection
    active_data_source = WebCrawlerDataSource()
    logger.info("Data source: %s", active_data_source.__class__.__name__)

    # 2) Build app
    app = build_app(active_data_source)
    logger.info("Tools registered")

    # Patch: Ensure port/host respects env var (FastMCP init defaults override env)
    env_port = os.getenv("FASTMCP_PORT")
    if env_port:
        try:
            app.settings.port = int(env_port)
            logger.info(f"Configured port from env: {app.settings.port}")
        except ValueError:
            logger.warning(f"Invalid FASTMCP_PORT: {env_port}, using default")

    env_host = os.getenv("FASTMCP_HOST")
    if env_host:
        app.settings.host = env_host
        logger.info(f"Configured host from env: {app.settings.host}")

    # 3) Initialize data source
    if active_data_source.initialize():
        logger.info("✅ Data source initialized successfully")
    else:
        logger.warning("⚠️ Data source initialization failed, functionality may be limited")

    def handle_sigterm(*args):
        logger.info("Received SIGTERM, cleaning up...")
        active_data_source.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    # 4) Run server (SSE mode)
    try:
        logger.info("🚀 Starting MCP Server (SSE)")
        # FastMCP uses uvicorn internally for SSE.
        # It reads host/port from FASTMCP_HOST and FASTMCP_PORT env vars.
        app.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("🛑 Server interrupted")
    except Exception:
        logger.exception("💥 Server error")
        raise
    finally:
        # 5) Cleanup resources
        try:
            active_data_source.cleanup()
            logger.info("🧹 Resources cleaned up")
        except Exception:
            logger.exception("💥 Resource cleanup error")

if __name__ == "__main__":
    main()
