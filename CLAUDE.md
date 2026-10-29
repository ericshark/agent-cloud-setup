# Cloud Agent Instructions

## Code Quality

- Keep changes focused on the request. Avoid unrelated modifications or unnecessary refactoring.

- Add comments when they explain non-obvious behavior, constraints, algorithms, or workarounds.

## Process Cleanup

Before completing a task:

- Terminate all long-running processes started during the task, including development servers, preview servers, watchers, and temporary background processes unless stated otherwise.
- Verify that ports used by processes started during the task have been released.
- Never leave a development server started by the agent running for the user unless stated otherwise.

## Git

- Before committing or pushing, verify the current branch and review the changes being staged. Do not overwrite remote changes or discard uncommitted work.
- Commit focused, completed changes automatically unless asked to leave them uncommitted. Run relevant checks when practical and disclose verification limits if any.
- Never commit secrets, credentials.
- Leave incomplete or blocked changes uncommitted and explain why. Ask if commit scope or readiness is unclear.
- Automatically push each completed commit to the assigned remote branch unless explicitly asked not to push. If the remote branch is unavailable push it or if the push fails, report the blocker.
- Never force-push, amend commits, rewrite history, or merge pull requests without explicit authorization.
  -Skipped checks do not automatically prevent a commit; use judgment based on the risk and disclose verification limits.
- After committing, end the final response commit hash, message, branch, and push status.

## Verification

- Run the relevant existing checks for the code changed when practical.
- Do not claim a test, build, lint, or type check passed unless it was actually run.
- Fix issues introduced by the task.
- If verification cannot be completed, clearly state what was not verified and why.

## Clarification

- Before starting a substantial or ambiguous task, consider whether a few clarifying questions would improve the outcome.
- Ask concise, relevant questions about requirements, expected behavior, scope, or important design decisions.
- For straightforward tasks or minor uncertainties, make reasonable assumptions and proceed.
- Avoid unnecessary questions when the answer is clear from the request or existing codebase.

## Completion

- When finished, give a summary of what you did, what you verified, and any important issues or limitations.
- If a check failed or a step was skipped, say so plainly.
- Include the pull-request URL if one was created.

## Environment limitations

- If required dependencies, services, credentials, or network access are unavailable, use supported alternatives when appropriate. Do not modify project configuration solely to work around cloud environment limitations. Report anything that could not be verified.

## UI Verification

- When needed, use the available Playwright skill to verify UI changes in a browser (headless with `PW_HEADLESS=true`).
- Check relevant viewport sizes, interactions, browser errors, and visual issues. Fix problems found.
- Report what was verified and any limitations.

## Pre-Deployment Performance Optimization

- Only invoke the `performance` skill when explicitly requested by the user.
- When invoked, audit the production build using the skill and available tools, including Lighthouse and Chrome DevTools MCP when available and appropriate.
- Identify, prioritize, and implement high-impact optimizations for loading speed, responsiveness, rendering, animations, and resource usage.
- Preserve the existing design, visual quality, interactions, and functionality.
- Avoid speculative micro-optimizations, unnecessary refactoring, and negligible improvements. Stop when further improvements are marginal.
- Re-run relevant audits, Playwright verification, and existing project checks after changes. Fix regressions and report before-and-after metrics and remaining significant issues.
- Do not claim production readiness unless the relevant checks have passed; report anything that could not be verified.
