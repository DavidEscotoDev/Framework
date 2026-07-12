#!/usr/bin/env python
"""
Quickstart example: Generate code using the Coding Agent programmatically.

Run with: python examples/quickstart.py
"""

import asyncio

from coding_agent.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
from coding_agent.config import Config
from coding_agent.llm.factory import get_provider, initialize_providers
from coding_agent.orchestrator import CodeOrchestrator
from coding_agent.schemas import GenerationRequest


async def main():
    # Load configuration
    cfg = Config()

    # Initialize LLM providers (reads API keys from env vars)
    def get_key(p):
        return cfg.get_provider_api_key(p)

    initialize_providers(cfg.llm.providers, get_key, cfg.llm.fallback_chain)
    llm = get_provider()

    # Create orchestrator and register agents
    orchestrator = CodeOrchestrator()
    orchestrator.register_agent("planner", PlannerAgent(llm, cfg.agents.planner))
    orchestrator.register_agent("coder", CoderAgent(llm, cfg.agents.coder))
    orchestrator.register_agent("reviewer", ReviewerAgent(llm, cfg.agents.reviewer))
    orchestrator.register_agent("tester", TesterAgent(llm, cfg.agents.tester))

    # Define your request
    request = "Create a Python class for a binary search tree with insert, search, and delete methods. Include type hints and docstrings."

    print(f"Generating code for: {request}\n")
    print("=" * 60)

    # Run the pipeline
    req = GenerationRequest(user_request=request)
    result = await orchestrator.generate_code(req)

    # Display results
    if result.code:
        print("GENERATED CODE:")
        print("-" * 60)
        print(result.code.code)
        print("-" * 60)

    if result.review:
        print(f"\nREVIEW SCORE: {result.review.quality_score}/100")
        if result.review.issues:
            print("ISSUES:")
            for issue in result.review.issues:
                print(f"  - {issue.severity}: {issue.message}")

    if result.tests:
        print(f"\nTESTS: {result.tests.passed} passed, {result.tests.failed} failed")
        if result.tests.failed > 0:
            for test in result.tests.details:
                if test.status == "failed":
                    print(f"  FAILED: {test.name} - {test.output}")

    if result.errors:
        print(f"\nERRORS: {result.errors}")


if __name__ == "__main__":
    asyncio.run(main())
