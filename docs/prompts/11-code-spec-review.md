# Code/Spec Review Prompt

Review `[FILES OR SPEC]` for correctness and risk.

Prioritize:
- Bugs and behavioral regressions
- Security/privacy issues
- Missing edge cases
- Missing tests
- Ambiguities that can cause wrong implementation

Output:
- Findings first, ordered by severity, with file/line refs when possible
- Open questions/assumptions
- Brief summary last
