# Contributing to Aegis

Short and strict because we have nine weeks.

## Branching

- `main` is always green and deployable
- Feature branches: `feat/<area>/<short-desc>` e.g. `feat/orchestrator/cascade-predictor`
- Bug fixes: `fix/<area>/<short-desc>`
- Chores: `chore/<short-desc>`

## Before you push

```bash
make lint
make test
```

Both must pass. If a test is flaky, mark it `@pytest.mark.flaky` and open an
issue — don't commit with a flake.

## Pull requests

- One PR = one logical change. No drive-by refactors in a feature PR.
- Title format: `<area>: <short description>`
- Description must include: what changed, why, how you tested it
- At least one teammate review before merge
- CI must be green — no exceptions

## Architectural decisions

If your change touches how services talk to each other, add an ADR under
`docs/decisions/` (copy the format of 0001). This is where we document
"why did we do it this way" for the judges and for us in 3 months.

## Secrets

Never commit anything in `.secrets/`, `.env`, or any file named
`service-account-*.json`. If you accidentally do, notify the team
immediately and rotate the credential.

## Code style

- Python: ruff (config in root `pyproject.toml`), strict mypy
- TypeScript: ESLint + Prettier, strict TS
- Dart: `dart analyze` + `dart format`
- SQL: sqlfluff

Auto-format on save is configured in `.vscode/settings.json` — use it.

## Commits

Conventional-commit style preferred but not enforced:

```
feat(orchestrator): add cascade predictor Phase 2 scaffold
fix(ingest): reject frames larger than 5MB
docs(architecture): update agent diagram
```

## Demo discipline

Never break `scripts/smoke.sh`. It's our "the project still works end-to-end"
check. If your PR breaks it, either fix it in the same PR or explicitly skip
the affected step with a comment explaining why and a linked issue.
