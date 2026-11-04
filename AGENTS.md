
# Cloud Agent Instructions

## Code Quality

- Keep changes focused on the request. Avoid unrelated modifications or unnecessary refactoring.
- Add comments only when they explain non-obvious behavior, constraints, algorithms, or workarounds.

## Process Cleanup

- Before completing a task, terminate development servers, watchers, and other long-running processes started during the task unless instructed otherwise.
- Verify that their ports have been released when practical.
- Do not leave agent-started servers running unnecessarily.

## Git and Branching

- Inspect the current branch, working tree, and remote before making Git changes. Preserve unrelated work and existing history.
- If the current branch is `work`, create and switch to a descriptively named `cloud-<feature-name>` branch before making changes.
- If the current branch is `main`, remain on `main`. If already on another branch, preserve it unless instructed otherwise.
- Automatically commit focused, completed changes unless explicitly told not to. Stage only relevant files.
- Run relevant checks when practical. Never commit secrets, unrelated changes, or knowingly broken or incomplete work. Disclose skipped verification.
- Do not push automatically. Push only when explicitly requested.
- Never force-push, amend, rewrite history, bypass protections, or merge pull requests without explicit authorization.
- Report the commit hash, message, branch, and push status after committing.

## Push and Deployment

- Use existing GitHub-connected hosting for deployments. Do not install hosting CLIs or create deployment infrastructure during ordinary cloud work.
- Before pushing, inspect the branch, intended changes, remote updates, and available deployment configuration. Never overwrite remote work.

### Production Branch (`main`)

- Always request explicit confirmation before pushing `main`, regardless of whether hosting is configured.
- Before asking, report the current branch and any verified existing production URL, or state that no production deployment is confirmed.
- Ask: **"You are on `main`. Pushing may update production. Would you like to continue?"**
- After confirmation, safely push the intended changes.
- If hosting is configured, check the resulting production deployment, commit, URL, and existing CI results. Return the verified production URL and status.
- If hosting is not configured, simply push and report that no deployment was confirmed.
- Investigate deployment or CI failures when possible. Never claim success without verification.

### Feature Branches

- When explicitly asked to push a non-production branch, push it to its matching remote branch without merging into `main`.
- After pushing, check GitHub Deployments and commit checks for the Vercel preview associated with the pushed commit.
- Wait for deployment completion when practical, then return the verified preview URL and status.
- Do not require the Vercel CLI or create an additional GitHub Actions workflow.
- If no preview deployment is configured, found, or verifiable, report that clearly. A successful Git push does not guarantee a deployment.
- If Git push access is unavailable, report the blocker and any supported alternative.

### Explicit Deployment Requests

- "Preview it" does not authorize an implicit Git push. Check an existing preview, or ask permission to push the branch if necessary.
- "Deploy it", "ship it", or "release it" means production.
- If production is requested from a feature branch, ask for confirmation before integrating the changes into `main`. Never silently merge or deploy a feature branch to production.
- If the required hosting integration or permissions are unavailable, report the limitation rather than installing tools or changing infrastructure.

## Verification

- Run relevant existing lint, type checks, tests, and builds when practical.
- Fix issues introduced by the task.
- Never claim a check passed unless it actually ran.
- Clearly report skipped or incomplete verification.

## Clarification

- Ask concise questions when important requirements, scope, or safety decisions are unclear.
- Otherwise, make reasonable assumptions and proceed without unnecessary interruptions.

## Completion

- Summarize changes, verification results, and important issues.
- Include commit hash, message, branch, and push status when relevant.
- After pushing, include the verified preview or production URL and deployment status when available.
- Include the pull-request URL if one was created.
- Clearly report failed or skipped checks and unresolved limitations.

## Environment Limitations

- Use available tools and permissions. If something is unavailable, explain the blocker and what is needed.
- Do not modify project configuration merely to work around cloud limitations.
- Never expose secrets, incur charges, or make destructive production changes without approval.

## UI Verification

- Use the available Playwright skill for substantial UI changes and at the end of a project or major feature affecting the UI. Run headlessly with `PW_HEADLESS=true`.
- For minor UI changes, use judgment rather than invoking Playwright automatically.
- Check relevant viewport sizes, interactions, browser errors, and visual issues. Fix problems and report verification results.

## Pre-Deployment Performance Optimization

- Invoke the `performance` skill only when explicitly requested.
- When invoked, audit the production build using available tools, including Lighthouse and Chrome DevTools MCP when appropriate.
- Prioritize high-impact improvements to loading, responsiveness, rendering, animations, and resource usage.
- Preserve existing design and functionality. Avoid unnecessary refactoring and negligible optimizations.
- Re-run relevant audits, Playwright verification, and project checks. Report before-and-after metrics and unresolved issues.
- Do not claim production readiness unless relevant checks have passed.
