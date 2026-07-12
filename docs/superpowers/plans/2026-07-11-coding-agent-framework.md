# Autonomous Coding Agent Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\- [ ]\) syntax for tracking.

**Goal:** Build a production-grade multi-agent system that generates, reviews, and tests Python code autonomously via a Planner -> Coder -> Reviewer -> Tester pipeline with multi-provider LLM support.

**Architecture:** Four specialized agents (Planner, Coder, Reviewer, Tester) coordinate via a CodeOrchestrator that passes SharedState sequentially. An LLM provider abstraction (NVIDIA NIM primary, OpenAI/Azure/Ollama fallbacks) handles text generation. Generated code executes in a tiered sandbox (subprocess+resource limits for dev, gVisor for production). Interfaces: Python library, FastAPI server (REST+WebSocket), and Typer CLI.

**Tech Stack:** Python 3.11+, Pydantic v2, FastAPI, asyncio, openai+httpx, pytest, structlog, opentelemetry, prometheus_client.

---

## Global Constraints

- Python 3.11+ only
- Pydantic v2+ for all data models
- All LLM providers interchangeable via ABC
- Every agent output MUST be a Pydantic BaseModel
- No sync I/O in async code paths
- API keys from environment variables only
- Code sandbox blocks: os, sys, subprocess, shutil, importlib, ctypes, multiprocessing, threading, socket
- Prompts are versioned file templates, not string literals
