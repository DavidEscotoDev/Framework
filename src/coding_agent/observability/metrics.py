from __future__ import annotations
from prometheus_client import Counter, Histogram, Gauge, start_http_server

pipeline_requests = Counter(
    "pipeline_requests_total",
    "Total pipeline requests",
    ["status"]
)

pipeline_latency = Histogram(
    "pipeline_latency_seconds",
    "Pipeline latency in seconds",
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

agent_latency = Histogram(
    "agent_latency_seconds",
    "Per-agent latency in seconds",
    ["agent"],
    buckets=[0.5, 1, 2, 5, 10, 30, 60]
)

llm_tokens = Counter(
    "llm_tokens_total",
    "Total LLM tokens consumed",
    ["provider", "model", "type"]
)

sandbox_executions = Counter(
    "sandbox_executions_total",
    "Sandbox executions",
    ["status"]
)

review_scores = Histogram(
    "review_scores",
    "Code review quality scores",
    buckets=[0, 20, 40, 60, 70, 80, 90, 100]
)

active_requests = Gauge(
    "active_requests",
    "Currently active pipeline requests"
)

def start_metrics_server(port: int = 9090):
    start_http_server(port)
