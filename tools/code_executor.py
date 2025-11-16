from google.adk.code_executors import BuiltInCodeExecutor


def build_code_executor() -> BuiltInCodeExecutor:
    """
    Build the BuiltInCodeExecutor that lets Gemini run Python code
    in a managed sandbox (no local code execution).
    """
    return BuiltInCodeExecutor()
