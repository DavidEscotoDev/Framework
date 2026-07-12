class CodingAgentError(Exception):
    def __init__(self, message: str, recoverable: bool = False):
        self.recoverable = recoverable
        super().__init__(message)

class AgentError(CodingAgentError):
    def __init__(self, agent_name: str, message: str, recoverable: bool = True):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}", recoverable)

class LLMProviderError(CodingAgentError):
    def __init__(self, provider: str, message: str, retry_after: int | None = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"[{provider}] {message}", recoverable=True)

class SandboxError(CodingAgentError):
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        super().__init__(f"[{error_type}] {message}", recoverable=False)

class ConfigError(CodingAgentError):
    def __init__(self, message: str):
        super().__init__(message, recoverable=False)
