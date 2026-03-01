---
name: Bug Report
about: Create a report to help us improve NexusBrain MCP
title: ''
labels: bug
assignees: ''
---

## Description
Provide a clear and concise description of the bug. Explain what is happening and why it is considered incorrect behavior.

## Steps to Reproduce
Please provide detailed steps to reproduce the issue:

1. Configure environment (e.g., specific Ollama model, SurrealDB version)
2. Run ingestion script with specific parameters
3. Invoke MCP tool (e.g., `semantic_code_search`)
4. Observe error or unexpected behavior

## Expected Behavior
Describe what you expected to happen. Include relevant details about the expected output, performance, or system state.

## Actual Behavior
Describe what actually happened. Include error messages, incorrect outputs, or system crashes.

## Environment
Please provide the following details about your environment:

- **Operating System:** [e.g. macOS 14.0, Ubuntu 22.04, Windows 11]
- **Python Version:** [e.g. 3.11.5]
- **SurrealDB Version:** [e.g. 1.0.0+20231020]
- **Ollama Version:** [e.g. 0.1.14]
- **Embedding Model:** [e.g. nomic-embed-text]
- **MCP Client:** [e.g. Claude Desktop, Cursor, Custom Client]
- **NexusBrain Version:** [e.g. 0.1.0 or specific commit hash]

## Logs and Errors
Paste any relevant logs, stack traces, or error messages here. Please use code blocks for formatting.

```text
Insert logs here
```

## Configuration
If applicable, provide relevant excerpts from your configuration files (e.g., `pyproject.toml`, `.env`, `claude_desktop_config.json`). Remove any sensitive information such as API keys or passwords.

## Additional Context
Add any other context about the problem here. This might include:
- Screenshots of the error
- Links to related issues or discussions
- Specific code snippets that trigger the bug
- Recent changes to the project structure or dependencies

## Potential Solution
If you have ideas on how to fix the issue or where the problem might originate (e.g., specific module in `src/nexusbrain/`), please share them here.
