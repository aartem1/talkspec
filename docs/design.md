# Design

## Goal and boundary

Create one portable communication specification for assistants, without personal data. Adapt presentation to tasks, not assumed characteristics of people. Support skills where available and self-contained instructions everywhere a host accepts them. Do not claim installation into unsupported consumer interfaces, strict STE conformance, guaranteed compliance, or new tool capabilities.

## Source and artifacts

`spec/rules.json` is the canonical core. Each rule holds full and compact wording. Six scenario files provide optional depth. `scripts/build.py` creates the portable skill, self-contained adapters, and a deterministic manifest. The skill links to only relevant references; always-on instructions include short scenario summaries, while the generic bot prompt includes the full scenarios. Compact instructions omit scenario detail deliberately.

The build enforces instruction-field budgets, rather than arbitrary limits on answers. The installer offers explicit always-on and on-demand modes and uses native documented paths. It refuses unsafe replacement and does not add broad triggers, permission directives, hooks, or network dependencies. This repository produces a reusable skill; it does not silently install it into the creator's personal skill account.

## Communication choices

Borrow clear sentences, consistent terminology, active verbs, gradual explanation, and bounded procedural steps from ASD-STE100 Issue 9. Do not adopt its controlled English dictionary or fixed sentence lengths as universal chat requirements. Keep technical precision and natural language in any language requested.

Borrow answer-first presentation, reduced tangents, visible relevant progress, and matter-of-fact failures from i-have-adhd. Do not adopt assumptions about diagnoses, mandatory recaps every turn, forced time estimates, or closing actions when the work is complete. These are presentation preferences, not clinical claims.

Use outcome-based instructions and explicit decision boundaries rather than detailed scripts for the model's reasoning. Research and verification effort should match the task's stakes. Explicit user requests can call for a long explanation, creative writing, an unusual format, or a different tone. Preserve host policy and permission constraints. Never treat these instructions as proof of authorization or as a replacement for domain expertise.

## Verification

Check generated artifacts, instruction budgets, self-contained links, metadata consistency, idempotent installation, preservation of unrelated content, modified-file refusal, path safety, and removal behavior. Maintain synthetic behavioral cases for language, ambiguity, evidence, depth, permissions, and failure recovery. Report host checks and model probes separately from deterministic tests; do not generalize a small probe to all models.

## Sources

Reviewed on 2026-10-02. Rules are newly written, not copied from a standard or another skill. Names and repository URLs identify technical sources and distribution endpoints, not a user profile.

- [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf), especially sections 1, 3–6, and 9.
- [i-have-adhd](https://github.com/ayghri/i-have-adhd), communication patterns and their trade-offs.
- [OpenAI prompting guidance](https://developers.openai.com/api/docs/guides/latest-model) and [revisiting skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
- [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) and [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
- Native formats: [installation references](installation.md#official-references).
