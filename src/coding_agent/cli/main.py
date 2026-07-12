from __future__ import annotations
import asyncio
import typer
from rich.console import Console
from ..config import Config
from ..llm.factory import initialize_providers, get_provider
from ..agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
from ..orchestrator import CodeOrchestrator
from ..schemas import GenerationRequest

app = typer.Typer(name="coding-agent", help="Multi-agent code generation system")
console = Console()

@app.command()
def generate(
    request: str = typer.Argument(..., help="The code generation request"),
    output: str = typer.Option("", "--output", "-o", help="Output file path"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json"),
):
    """Generate code from a natural language request."""
    async def _run():
        cfg = Config()
        def get_key(cfg):
            return cfg.get_provider_api_key(cfg)
        initialize_providers(cfg.llm.providers, get_key, cfg.llm.fallback_chain)

        llm = get_provider()
        orchestrator = CodeOrchestrator()
        orchestrator.register_agent("planner", PlannerAgent(llm, cfg.agents.planner))
        orchestrator.register_agent("coder", CoderAgent(llm, cfg.agents.coder))
        orchestrator.register_agent("reviewer", ReviewerAgent(llm, cfg.agents.reviewer))
        orchestrator.register_agent("tester", TesterAgent(llm, cfg.agents.tester))

        req = GenerationRequest(user_request=request)
        result = await orchestrator.generate_code(req)

        if format == "json":
            console.print_json(result.model_dump_json(indent=2))
        else:
            if result.code:
                console.print(f"[bold green]Generated Code:[/]")
                console.print(result.code.code)
                if result.review:
                    console.print(f"[bold]Review Score:[/] {result.review.quality_score}/100")
                    if result.review.issues:
                        console.print(f"[red]Issues: {len(result.review.issues)}[/]")
                if result.tests:
                    console.print(f"[bold]Tests:[/] {result.tests.passed} passed, {result.tests.failed} failed")
            if result.errors:
                console.print(f"[red]Errors: {result.errors}[/]")

            if output:
                with open(output, "w") as f:
                    f.write(result.code.code if result.code else "")
                console.print(f"[green]Written to {output}[/]")

    asyncio.run(_run())

@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind host"),
    port: int = typer.Option(8000, "--port", "-p", help="Bind port"),
):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run("coding_agent.api.server:create_app", host=host, port=port, factory=True)

@app.command()
def config():
    """Show current configuration."""
    import yaml
    cfg = Config()
    console.print(yaml.dump(cfg.model_dump(), default_flow_style=False))

if __name__ == "__main__":
    app()
