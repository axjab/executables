---
name: bash-engineering
description: Design, implement, refactor, review, and test production-quality Bash scripts and Linux automation. Use for Bash CLIs, bootstrap scripts, service checks, system diagnostics, maintenance utilities, and shell scripting code reviews. Prioritizes minimal, composable design, correct failure handling, security, testability, and verified delivery.
metadata:
  version: "1.0.0"
---

# Bash Engineering

Develop Bash that a Linux systems engineer can read, operate, test, and extend. Optimize for **correct behavior and low maintenance cost**, not cleverness or line count alone. Apply this skill when writing or reviewing Bash; adapt all choices to the user's explicit requirements and target environment.

## 1. Non-negotiable contract

1. **Specify before implementing.** Identify purpose, platform/Bash version, inputs, outputs, side effects, dependencies, failure policy, and exit-code semantics. If an unresolved ambiguity would change correctness or safety, ask; otherwise state reasonable assumptions and proceed.
2. **Use the least complex adequate design.** Prefer a single script with small functions until additional files or abstractions pay for themselves. Never add a framework, generic plugin system, or configuration format without a concrete need.
3. **Separate responsibilities.** A function should perform one coherent task and have an intelligible name. Separate data collection, policy decisions, serialization, and presentation when the program needs these layers. Avoid repeating equivalent logic.
4. **Make failures explicit.** Never confuse missing evidence, command failure, permission denial, or malformed data with success. Check all required operations, preserve meaningful errors, and use explicit exit codes.
5. **Design for verification.** Make external effects replaceable in tests, test successful and failed paths, and run available validation tools before claiming completion.
6. **Respect the interface.** Produce exactly the requested output format and preserve established CLI behavior unless asked to change it. Never let diagnostic chatter pollute machine-readable stdout.
7. **Do not fabricate confidence.** Report what was actually inspected, executed, tested, and not tested. If verification tools are unavailable, say so.

These are behavioral requirements, not an excuse to over-engineer. Treat SOLID as a guide to cohesion and dependency boundaries, not an instruction to imitate object-oriented patterns in Bash.

## 2. Required workflow

### A. Define the contract

Before coding, resolve or record:

- Supported distribution(s), shell/Bash version, privilege expectations, and available commands.
- Invocation syntax, defaults, flags, arguments, input sources, and help behavior.
- stdout versus stderr, formatting rules, output schema if applicable, and whether output is stable for scripts.
- Exit statuses: success, expected policy failures, usage/dependency errors, and partial/unknown results.
- State changes (files, users, services, firewall, network); define safe retry and idempotency when relevant.
- Security assumptions and the difference between **observed state** and **required policy**.

Ask for clarification only when proceeding would require choosing between materially different or unsafe behaviors. Do not silently invent security policy.

### B. Design the smallest decomposition

- Put user-editable settings near the start of the module unless a separate config format is explicitly required.
- Define `main()` near the top, after configuration, and call it at the bottom; define helper functions between those locations. Bash resolves functions when `main` is invoked, so this works.
- Keep `main()` as an orchestration outline rather than a large implementation block.
- Keep collection functions independent. Make transformations and decisions pure where practical.
- Introduce generic helpers only when they eliminate genuine repetition or define a meaningful boundary.
- Group related code by responsibility; avoid creating one-line wrappers that obscure rather than clarify.

Preferred executable shape:

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly VERSION='1.0.0'

main() {
    parse_args "$@"
    check_dependencies
    run_workflow
}

# Small, focused functions follow here.

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    main "$@"
fi
```

The skeleton is illustrative: do not add unused functions or variables. Preserve the source guard when the script's functions will be sourced for tests; avoid executing `main` during import.

### C. Implement idiomatic, defensive Bash

- Prefer Bash builtins, arrays, `[[ ... ]]`, arithmetic contexts, `case`, and explicit functions over dense pipelines or regex tricks.
- Quote expansions (`"$value"`, `"${array[@]}"`); use arrays for argument vectors, not space-separated command strings. Use `--` for operands where supported.
- Use `local` for function variables. Keep globals largely limited to configuration/constants. Avoid `eval`, implicit word splitting, unsafe globbing, and parsing `ls`.
- Use `read -r`, correct `IFS`, and NUL delimiters (`-print0`, `read -d ''`) for arbitrary filenames. Distinguish data from shell code.
- Default to `set -euo pipefail` for programs; add `-E` only when an inherited `ERR` trap is actually needed. Do **not** assume `errexit` handles every failure: conditions, `&&`/`||`, subshells, and command substitutions have exceptions. Handle expected nonzero statuses deliberately.
- Do not hide important statuses through `|| true`, `|| :`, uninspected pipelines, or `local x=$(command)`; declare and assign separately when status matters.
- Use explicit `if command; then ... else ... fi` for expected unsuccessful probes (e.g., `grep`, `systemctl`, `curl`). Do not globally disable strict mode to accommodate them.
- Keep error messages actionable and send errors to stderr; do not print secrets or sensitive command output.
- Check external dependency availability, permissions, timeouts, and malformed or missing responses. Use structured parsers (e.g., `jq` for JSON) instead of brittle text scraping when possible.
- For temporary files use `mktemp` with cleanup traps. Do not overwrite user files without a clear contract; use atomic writes when interruption could corrupt state.
- Quote trap behavior carefully. Preserve original failure codes when cleaning up. Handle interrupts where long-running work or child processes require it.
- Avoid sourcing untrusted input, logging credentials, interpolating unsanitized values into commands, or passing secrets unnecessarily through argv.

**Correctness beats concision.** Ten difficult lines are not automatically better than twenty obvious ones. Conversely, abstraction that does not improve clarity, testing, or reuse should be removed.

### D. Specify and test behavior

Before calling the script complete, test a representative matrix:

| Area | Minimum cases |
| --- | --- |
| CLI | Defaults, help, invalid flag, extra arguments |
| Data | Valid, missing, malformed, empty, and unusual values |
| External commands | Success, nonzero exit, unavailable command, timeout, denied permission |
| Policy | Healthy, warning, failure, and unverifiable/unknown condition where relevant |
| Output | Schema, escaping, no unsolicited stdout, redirected/non-TTY behavior |
| Lifecycle | Re-run/idempotency for mutating scripts; cleanup/interrupts when applicable |

Use fixtures and fake executables injected through `PATH`, or explicit command adapters, so tests do not need real network access, root privileges, or changes to the host. Prefer a few meaningful tests over a large number of tests that merely confirm implementation details.

Run, when available:

```bash
bash -n path/to/script
shellcheck path/to/script
# Run the repository's actual test command (Bats or a shell test harness).
```

For reporting CLIs also verify JSON parses and check exit codes deliberately. Never label a test as passed unless it ran successfully. Missing ShellCheck or unavailable infrastructure is an **unverified gate**, not a pass.

### E. Review before delivery

Perform a focused adversarial review:

- Are any security states declared healthy merely because the check failed or lacked permission?
- Could `set -e`, a subshell, pipeline, or suppressed stderr cause a surprising early exit or false result?
- Do stdout, stderr, and exit codes retain the documented contract on every branch?
- Are quoting, arrays, pathnames containing spaces, and untrusted responses handled safely?
- Can a failed/interrupted write leave a partially changed system?
- Are the smallest sensible units testable without production resources?
- Is there duplicated logic, hidden coupling, an unnecessary dependency, or speculative abstraction?
- Does the documentation reflect actual behavior and known limitations?

Fix material issues and repeat relevant tests. Deliver the implementation and a brief verification report: **checks executed, results, remaining limitations**.

## 3. Optional profile: JSON-first diagnostics and styled reports

Activate this profile **only when a program produces diagnostics, structured status reports, or when the user explicitly requests it**. Do not force installers, filters, or simple utilities to return JSON.

When active:

1. Each check produces structured data with a stable identity, section, status, human-readable label, and value or explanation. Prefer `ok`, `warn`, `fail`, `info` as distinct statuses.
2. Preserve the distinction between **observation** (`info`) and **policy result** (`ok`/`warn`/`fail`). An unknown location does not prove privacy; an unreachable security service does not prove protection.
3. Aggregate **all independent results** into one canonical JSON document before presentation. Do not allow a failed policy check to short-circuit unrelated checks; execution errors may halt only when further results cannot be meaningful.
4. Implement pretty output as an optional renderer that reads the aggregated JSON. The renderer must not run probes or recompute policy.
5. Provide `--json` when requested; JSON must parse cleanly with `jq` and contain no progress bars, log messages, colors, or other stdout noise. Errors go to stderr or into the agreed JSON envelope.
6. If color is enabled, enable it only for an interactive terminal and when `NO_COLOR` is unset. Never emit ANSI escapes in JSON output.
7. Keep statuses and exit codes consistent: for the host-doctor convention, `0` means no failed checks (warnings permitted), `1` means a failed policy check, and `2` means usage/dependency/execution error. Use a different mapping if the CLI specification calls for it.
8. Prefer one network request for multiple fields from the same endpoint, parse JSON once, and reuse validated data. Set explicit connection and overall timeouts.
9. Treat counters consistently; define whether informational items count toward the human-readable `ok` total. Avoid inventing or inflating counts.
10. If requested, use DMS-style colored `●` / `○` marks and `N warning(s), N ok` footer **only in the renderer**. Icons and colors are presentation, not semantic data.

Example check record (illustrative schema, not a universal standard):

```json
{
  "section": "Privacy",
  "id": "vpn_exit",
  "label": "VPN exit IP",
  "status": "fail",
  "value": "Not verified"
}
```

Prefer a canonical report wrapper containing tool/version, checks, and summary counts. Version or document its schema if downstream programs will consume it.

## 4. Stop conditions and delivery rules

- **Stop and ask** if required destructive behavior, privilege assumptions, security policy, or output semantics are materially unspecified and a guess could cause harm or break the user's contract.
- **Do not silently downgrade** required verification, bypass safeguards, alter requested output, or add unrequested dependencies.
- **Do not substitute** mock success for live verification; mocks establish control-flow correctness, not external-service availability.
- **If time/tools prevent full validation**, deliver the best complete implementation possible and explicitly enumerate unverified behavior. Do not claim production readiness without evidence.
- **When revising existing code**, preserve the observable interface unless a change is requested, and provide regression coverage for the affected behavior.

Quality is demonstrated through small, comprehensible code, accurate status reporting, meaningful tests, and explicit limits—not by asserting that the script is "production-grade."
