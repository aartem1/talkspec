# Behavioral evaluation

`cases.jsonl` contains synthetic prompts and acceptance criteria. No real user conversations, identities, or health records are included. The cases are not golden answers: evaluate meaning, completeness, and evidence rather than matching exact wording.

For each model/host, compare the same cases with and without TalkSpec under the same tools and permissions. Record model/version, date, host, activated instruction artifact, tool availability, outputs, and observed failures. Evaluate each criterion as pass, partial, or fail; report failures rather than hiding them in an average. The build tests are separate and do not score model behavior.

Check that the relevant artifact is actually loaded. Test both short and detailed requests, no-tool settings, a missing consequential choice, and an authorized action. For safety-sensitive prompts use mocks or disposable local fixtures, not real purchases, publication, deletions, or credentials.

Prompt improvements should follow observed failures: change the smallest relevant rule, regenerate adapters, and rerun the same cases. Do not reward brevity when it deletes requested content. Do not use a single model to certify every adapter.

No paid model requests or live client integration tests run automatically. Independent probes conducted during initial development are described in `development-checks.md` with their limitations.
