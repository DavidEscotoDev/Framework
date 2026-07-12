# Multi-stage build for coding-agent
FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml config.yaml .env.example ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY config.yaml ./

RUN pip install --no-cache-dir -e .[dev]

# Production stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Create non-root user
RUN useradd -m -u 1000 coding-agent
USER coding-agent

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "uvicorn", "coding_agent.api.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
