FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# Set work directory
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Sync dependencies using uv
RUN uv sync --frozen

# Create a non-root user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 --home /app appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose port (default for FastMCP)
EXPOSE 8001

# Set default environment variables for FastMCP
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8001
# Ensure Python path includes src
ENV PYTHONPATH=/app/src

# Run the application
CMD ["uv", "run", "python", "-m", "stock_mcp.sse"]
