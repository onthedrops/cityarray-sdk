# Red-Team Review Prompt

Red-team `[PLAN/FEATURE/SYSTEM]` aggressively.

Do:
- Attack assumptions.
- Identify failure paths (technical, product, compliance, operational).
- Find easiest ways this can break or be abused.
- Quantify severity and confidence.

Output format:
1. Findings ordered by severity.
2. Exploit scenario for each finding.
3. Concrete mitigations.
4. Residual risks after mitigation.
