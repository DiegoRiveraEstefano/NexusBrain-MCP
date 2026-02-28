# Contribution Guide (NexusBrain MCP)

Thank you for your interest in contributing to NexusBrain MCP. This project aims to establish the gold standard for integrating GraphRAG and MCP in local development environments.

To maintain code quality and a comprehensible project history, the following guidelines have been established for reporting issues, creating branches, and submitting changes.

---

## 1. Issue Management (Bugs and Features)

Before writing code, ensure that an open Issue exists for the work you intend to perform.

* **Bugs:** Clearly describe the error, steps to reproduce, expected behavior, and your environment (operating system, Python version, SurrealDB version).
* **New Features:** Explain the rationale ("why") and the proposed implementation approach ("how"). If proposing a new MCP Tool, detail the token efficiency gains or the specific cognitive challenge it addresses for the AI assistant.
* **Assignment:** Comment on the Issue to indicate your intention to work on it, preventing duplicate efforts.

---

## 2. Branching Strategy

This project follows a **Feature Branch** workflow. Direct commits to the `main` branch are not permitted.

### Branch Naming Convention
Branch names should clearly indicate their purpose and reference the associated Issue number.
Format: `<type>/<issue-number>-<short-description>`

Allowed types:
* `feat/` – New features or tools.
* `fix/` – Bug fixes.
* `docs/` – Documentation updates.
* `refactor/` – Code refactoring (without altering external behavior).

**Valid Examples:**
* `feat/12-add-blast-radius-tool`
* `fix/45-surrealdb-connection-timeout`
* `docs/8-update-readme-architecture`

---

## Atomicity and Commits

### Atomic Commits
Each commit should address **a single concern** and leave the project in a functional state.
* *Avoid:* A single commit that adds a RAG tool, reformats five files, and fixes a connection bug.
* *Preferred:* Three separate commits, each addressing one of these changes independently.

### Commit Message Convention (Conventional Commits)
Commit messages should be readable by both humans and automated tools (e.g., for generating changelogs). Please adhere to the following format:

```text
<type>(<optional scope>): <imperative description>

[optional body providing context or rationale for the change]

[optional footer referencing the issue, e.g., Closes #12]
```

**Examples:**
```text
feat(search): add semantic code search tool

Implements vector-based search functionality using Ollama embeddings.
This enables the AI assistant to retrieve relevant code snippets based
on natural language queries.

Closes #23
```

```text
fix(db): handle connection retry logic in SurrealDB client

Adds exponential backoff for transient connection failures.
Improves resilience during local development environments with
intermittent database availability.

Closes #45
```

---

## 3. Pull Request Process

1. **Fork and Clone:** Fork the repository and clone your fork locally.
2. **Create a Branch:** Follow the branching convention described above.
3. **Develop and Test:** Implement your changes and ensure all tests pass (`pytest`).
4. **Update Documentation:** If applicable, update relevant documentation or add new examples.
5. **Submit a Pull Request:** Open a PR against the `main` branch with:
   * A clear title following the Conventional Commits format.
   * A description summarizing the changes, referencing the associated Issue.
   * Checklist items confirming tests pass and documentation is updated.

---

## 4. Code Style and Quality Standards

* **Type Hints:** Use Python type annotations for all function signatures.
* **Documentation:** Include docstrings for public modules, classes, and functions (Google or NumPy style).
* **Testing:** New features or bug fixes should include corresponding unit or integration tests.
* **Linting:** Ensure code passes `ruff`/`black` formatting and `mypy` type checking before submission.

---

## 5. Review and Merge Criteria

Pull requests will be reviewed based on:
* - Alignment with the stated Issue scope.
* - Adherence to architectural patterns and separation of concerns.
* - Test coverage and passing CI checks.
* - Clear, maintainable, and well-documented code.

Once approved, changes will be merged by a maintainer. Squash merging is preferred to maintain a clean linear history.

---

*By contributing to NexusBrain MCP, you agree to license your contributions under the project's specified license.*
