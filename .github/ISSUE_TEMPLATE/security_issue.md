---
name: Security Issue
about: Report a vulnerability or security concern in NexusBrain MCP
title: '[SECURITY] '
labels: security
assignees: ''
---

## Important Notice Regarding Responsible Disclosure

If you believe you have discovered a critical security vulnerability that could expose user data or compromise system integrity, please consider contacting the maintainers privately before opening a public issue. This allows us to develop and deploy a fix before details are publicly available.

**For sensitive reports, please contact:** [security@nexusbrain.example.com] (Replace with actual contact)

If you are certain this issue can be disclosed publicly without immediate risk, please proceed with the template below.

---

## Vulnerability Description
Provide a clear and concise description of the security vulnerability. Explain the nature of the weakness (e.g., injection, authentication bypass, data leakage, insecure dependency).

## Vulnerability Type
Categorize the issue if possible (e.g., OWASP Top 10, CWE ID).
- **Type:** [e.g., SQL Injection, Insecure Deserialization, Improper Access Control]
- **CWE ID:** [e.g., CWE-89] (Optional)

## Severity Assessment
Please provide your assessment of the severity level.
- [ ] Critical (Remote code execution, full data breach)
- [ ] High (Significant data loss, privilege escalation)
- [ ] Medium (Limited data exposure, denial of service)
- [ ] Low (Minor information leakage, best practice violation)

## Affected Components
Identify the parts of the system affected by this vulnerability.
- **Module:** [e.g., src/nexusbrain/db/, src/nexusbrain/tools/]
- **Version:** [e.g., 0.1.0, main branch]
- **Configuration:** [e.g., Specific SurrealDB setup, Ollama configuration]

## Steps to Reproduce
Provide a sanitized version of the steps required to reproduce the vulnerability. **Do not include sensitive data, real API keys, or personal information in this section.**

1.
2.
3.

## Potential Impact
Describe the potential consequences if this vulnerability is exploited.
- **Confidentiality:** [e.g., Unauthorized access to codebase embeddings]
- **Integrity:** [e.g., Ability to modify decision logs]
- **Availability:** [e.g., Denial of service via malformed MCP requests]

## Suggested Mitigation
If you have a proposed fix or mitigation strategy, please describe it here. Include code snippets or configuration changes if applicable.

## References
Provide links to any relevant documentation, advisories, or similar vulnerabilities.

## Additional Context
Add any other information that might help in assessing and resolving this issue.

---

*By submitting this report, you agree to act in accordance with responsible disclosure practices. We appreciate your help in keeping NexusBrain MCP secure.*
