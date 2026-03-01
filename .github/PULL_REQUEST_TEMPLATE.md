## Description
<!-- Provide a concise summary of the changes introduced by this PR. What problem does it solve? Why is this approach preferred? -->

## Related Issue
<!-- Link to the issue this PR addresses. Use keywords like "Closes", "Fixes", or "Resolves" to auto-close upon merge. -->
Closes #<issue_number>

## Type of Change
<!-- Mark the appropriate option with an [x]. Remove options that don't apply. -->
- [ ] `feat` – New feature or MCP tool
- [ ] `fix` – Bug fix (non-breaking change)
- [ ] `docs` – Documentation update only
- [ ] `refactor` – Code improvement without behavior change
- [ ] `test` – Adding or updating tests
- [ ] `perf` – Performance optimization
- [ ] `chore` – Build process, tooling, or maintenance

## MCP-Specific Considerations
<!-- If this PR introduces or modifies MCP tools, complete this section. -->
- [ ] Tool name follows `snake_case` convention
- [ ] Docstring is clear, complete, and LLM-readable (explains purpose, parameters, returns)
- [ ] Input validation uses Pydantic models or strict type hints
- [ ] Tool is registered in `main.py` and exposed via `@server.tool()`
- [ ] No blocking calls (`time.sleep`, `requests`) in async tool implementations

## Implementation Details
<!-- Describe the technical approach. Include architecture decisions, data flow changes, or new dependencies. -->

### Key Changes
-
-
-

### Data Model Updates (if applicable)
<!-- Describe any changes to SurrealDB schema, nodes, or edges. -->
-

## Testing
<!-- Explain how changes were validated. Include commands to reproduce test scenarios. -->

### Test Coverage
- [ ] Unit tests added/updated (`tests/`)
- [ ] Integration tests added/updated (`tests/integration/`)
- [ ] Async tests use `@pytest.mark.asyncio`
- [ ] External dependencies mocked appropriately

### Manual Validation Steps
```bash
# Example: Run ingestion script
python scripts/ingest_repo.py --path ./test-project

# Example: Test MCP tool via CLI
mcp call semantic_code_search --query "authentication logic"
```

## Code Quality Checks
<!-- Confirm all validation steps pass before requesting review. -->
- [ ] `ruff check src/ tests/` – No linting errors
- [ ] `ruff format src/ tests/` – Code properly formatted
- [ ] `mypy src/` – Type checking passes (100% hint coverage)
- [ ] `pytest tests/ -v` – All tests pass
- [ ] Docker build succeeds: `docker build -t nexusbrain-mcp .`

## Documentation Updates
- [ ] Docstrings updated for public functions/classes
- [ ] `README.md` reflects new features or usage changes
- [ ] `ARCHITECTURE.md` updated if data flow or modules changed
- [ ] `AGENTS.md` updated if AI interaction patterns affected

## Breaking Changes
<!-- If this PR introduces breaking changes, describe them and migration steps. -->
- [ ] No breaking changes
- [ ] Breaking changes present (details below)

<details>
<summary>Breaking Change Details (if applicable)</summary>

<!-- Describe what breaks, who is affected, and how to migrate. -->

</details>

## Screenshots / Logs (if applicable)
<!-- For UI changes or observable behavior modifications, include relevant output. -->

## Reviewer Checklist
<!-- For maintainers reviewing this PR -->
- [ ] Changes align with the referenced Issue scope
- [ ] Architecture patterns respected (modularity, async-first, type safety)
- [ ] MCP tool docstrings enable reliable LLM discovery and usage
- [ ] Tests cover success and error paths
- [ ] No unintended side effects on ingestion or query performance
- [ ] Dependencies added only when necessary and justified

## Post-Merge Actions
<!-- Any follow-up tasks required after merging (e.g., documentation deployment, version bump). -->
- [ ] None
- [ ] Update changelog
- [ ] Notify downstream consumers
- [ ] Other: _______________

---

*By submitting this PR, I confirm that my contributions comply with the [Contribution Guide](CONTRIBUTING.md) and [Style Guide](STYLE_GUIDE.md), and I agree to license my work under the project's MIT License.*
