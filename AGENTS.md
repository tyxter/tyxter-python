# AGENTS.md

Repository-wide instructions for coding agents. A deeper `AGENTS.md` overrides this file only for
its subtree. Executable configuration and generated contract artifacts outrank prose when they
disagree.

## Project

`tyxter-python` is the typed, synchronous Python SDK for [Tyxter Messaging](https://tyxter.com),
built for both human developers and integrating agents. It is a downstream implementation of the
canonical TypeScript/JavaScript SDK, published on npm as
[`tyxter`](https://www.npmjs.com/package/tyxter) since 0.11.0. The former `@tyxter/sdk-js` package
stops at 0.10.0.

The canonical SDK source lives in Tyxter's private `tyxter-messaging` repository under
`packages/sdk-js/`. The npm package proves what was actually published; the corresponding release
tag, source, tests, README, and changelog in the private repository define the behavior to port.
The public API contracts and generated endpoint/query snapshots in that repository define the wire
contract.

Python is not an independent product surface. Use Python idioms at the call site, but preserve the
canonical SDK's capabilities and the API's exact wire behavior.

## Mandatory release parity

Every published `tyxter` npm release starts a Python parity update. The Python SDK must be
updated to the same version line; do not intentionally leave it behind or treat a conformance-only
snapshot refresh as a completed update.

At the start of SDK or release work:

1. Run `npm view tyxter version dist-tags --json` to learn what npm actually serves.
2. Compare it with `src/tyxter/_version.py` and the latest Python changelog entry.
3. In an authorized checkout of the private `tyxter-messaging` repository, locate the matching
   `sdk-js-v<version>` tag and read `packages/sdk-js/package.json`, `CHANGELOG.md`, `README.md`,
   public source, and tests. A version bump or changelog section without a published npm version
   is not a release.
4. Diff the new canonical tag from the last canonical version represented by Python. Inventory all
   public methods, options, request/response fields, exported types, errors, webhook contracts,
   headers, query parameters, and documentation changes—not just new routes.

A Python version means full parity with that canonical version. A documentation- or metadata-only
re-upload of a released version uses a PEP 440 post-release (`X.Y.Z.postN`) with no code change
(owner, 2026-11-06). If complete parity is blocked, keep
the work unreleased and report the precise gap. Canonical changes that have not shipped on npm may
be prepared only as clearly labelled `Unreleased` work; never describe them as published behavior.

## Parity contract

- Match every supported canonical resource and method. Python method and keyword names are
  `snake_case`; HTTP paths, query names, headers, JSON keys, omission/null behavior, and response
  semantics remain exact.
- Mirror request and response types precisely with `TypedDict`, `Literal`, unions, and
  `NotRequired` as appropriate. Do not replace a known shape with `Any` or generic JSON merely to
  make a port easier.
- Preserve source and runtime compatibility for existing Python callers. Additive response fields
  should remain forward-compatible. Removing or renaming a public method, field, callable type, or
  stable `error.code` requires an explicit deprecation decision.
- Keep public exports complete. Types belong in `src/tyxter/types/` and its export surface;
  resources belong in `src/tyxter/resources/` and are exposed through `Tyxter` using established
  patterns. Update top-level exports when the existing API convention calls for them.
- Match canonical idempotency modes exactly: `unsupported`, `supported`, or `required`. Never add
  an idempotency argument to an unsupported route, silently generate a key for a caller-required
  operation, accept a blank required key, or spend a retry before local validation fails.
- Match `Tyxter-Trace-Id` support exactly. Preserve API status, body, stable error codes,
  `Retry-After`, and typed error details rather than inventing client-side semantics.
- Keep the SDK synchronous and based on the existing `httpx` transport. Do not add a dependency or
  an async/public convenience surface as part of parity work without an explicit decision.
- Add or update README examples when a new public feature needs usage guidance. Examples must use
  public APIs, redacted placeholders, and accurate delivery/security caveats.

## Canonical conformance artifacts

`conformance/public-api-launch-endpoints.json` and
`conformance/public-api-query-params.json` are generated in `tyxter-messaging`. Copy them exactly
from the canonical commit being targeted and write that commit's full SHA to
`conformance/SOURCE_COMMIT`.

Never hand-edit snapshot rows, delete a route, loosen an assertion, or add an exemption to make CI
green. A red `tests/test_route_conformance.py` after a snapshot sync is a drift alarm: implement or
correct the SDK surface. The two capability-token media blob routes are reviewed exemptions because
the public `media.upload` flow owns them; any new exemption requires an explicit contract review.

The messaging repository's `sync-python-sdk-manifest.yml` workflow may open or update a manifest PR
here. Treat that PR as the start of parity work, not as a mechanical JSON-only change. If
`SDK_PYTHON_SYNC_TOKEN` is absent or invalid, report it as an external automation prerequisite; do
not commit a credential or weaken the gate.

## Repository map

```text
src/tyxter/client.py          public Tyxter client and resource wiring
src/tyxter/resources/        HTTP methods and wire serialization
src/tyxter/types/            public typed request/response contracts
src/tyxter/message_builders.py
                              channel payload helpers
src/tyxter/errors.py          runtime and typed API errors
src/tyxter/webhooks.py        webhook verification
conformance/                  byte-copied canonical contract snapshots + source SHA
tests/test_route_conformance.py
                              route/query/header drift gate
tests/test_typing_contracts.py and tests/typing/
                              strict public typing corpus
tests/test_distribution.py   wheel/sdist contents and metadata
examples/                     deterministic public-API examples
```

Read the resource, adjacent types, exports, and focused tests together before editing. Reuse
`BaseResource._request`, `path_id()`, pagination shapes, omission rules, and existing validation
patterns rather than creating parallel abstractions.

## Implementing a canonical release

For each new canonical release:

1. Record the published JS version, canonical release tag/commit, and the previous Python parity
   baseline.
2. Port the complete release diff. Update resources, precise types, exports, builders, error and
   webhook handling, docs, and tests as applicable.
3. Refresh both conformance snapshots from one canonical commit and update `SOURCE_COMMIT`. Never
   mix artifacts from different revisions.
4. Add focused request-construction tests for exact method, encoded path, query, JSON body, and
   supported headers. Add response/runtime tests and strict typing-corpus cases for new unions or
   public types. A test should fail against the pre-port implementation.
5. Update `CHANGELOG.md`, `README.md`, `src/tyxter/_version.py`, and version-sensitive distribution
   assertions together. Keep `Unreleased` changes distinct from the newly released canonical
   section.
6. Run the complete local gate and inspect the full diff for omitted canonical surface,
   compatibility breaks, hand-edited generated data, secrets, and unrelated cleanup.
7. Report the canonical version and SHA used, the parity surface covered, exact verification
   results, and any remaining publication or automation prerequisite.

Do not claim parity based only on route counts. Route, query, and header equality are necessary;
types, runtime serialization, public exports, errors, webhooks, docs, and compatibility complete the
contract.

## Development conventions

- Python support, dependencies, Ruff rules, and strict mypy configuration live in
  `pyproject.toml`; `uv.lock` is authoritative for the development environment.
- Use `uv`; do not create a second lockfile or casually widen dependency ranges.
- Format to Ruff's 100-column configuration and retain strict typing. Do not suppress or weaken a
  lint/type error to avoid modeling the public contract.
- Keep changes focused. Do not combine a parity update with unrelated cleanup or broad formatting.
- Tests must be deterministic and must not call Tyxter, Meta, npm, PyPI, or other live services.
  Use the existing mock `httpx` transport and fixtures.
- Never place API keys, npm/PyPI/GitHub tokens, customer identifiers, payloads, or unredacted
  environment values in source, tests, logs, screenshots, or docs.

## Verification

Run focused tests while developing, then the full gate before handoff:

```bash
uv sync --locked --extra dev
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked pytest
```

For a release candidate, also run `uv build`, inspect the wheel and sdist contents, and install the
built wheel into a fresh temporary environment. Confirm the imported `tyxter.__version__`, public
exports, `py.typed`, README, changelog, and license. Do not leave `dist/`, temporary environments,
or other generated artifacts in the commit.

CI runs the full gate on every Python version listed in its matrix. Report commands and results
exactly; if a gate cannot run because an authorized canonical checkout, service, or credential is
unavailable, state that instead of presenting partial evidence as green.

## Publishing and git safety

Updating parity and publishing to PyPI are separate actions. Do not create or push a `v*` tag,
dispatch `.github/workflows/publish.yml`, upload an artifact, merge, or otherwise publish unless the
user explicitly authorizes that release action and target. Never run a manual PyPI upload; the
repository workflow uses Trusted Publishing and verifies main ancestry, version/channel agreement,
the full Python matrix, package contents, and duplicate-release state.

The workflow refuses to upload a version whose `## [<version>]` section in `CHANGELOG.md` is
missing or has no entries, or when tag `v<version>` exists on a commit other than the one being
published. After the PyPI upload it creates the GitHub release `v<version>` from that section,
marked as a prerelease for a prerelease version (the alpha channel); if the release already exists,
it leaves it unchanged. A manual dispatch without tag `v<version>` still publishes to PyPI but
creates no release and ends with a warning. To retry a failed release step, use **Re-run failed
jobs**, which repeats only the release. A full rerun, or the run that starts when you push the
tag after such a dispatch, stops at the PyPI duplicate check by design. In that case, create the
release by hand with the `gh release create` command printed in the warning.

Preserve unrelated user changes. Do not discard edits, rewrite history, force-push, or use
destructive Git commands. Do not commit, push, or open a PR unless requested or required by the
active workflow. Before handoff, review `git diff` and `git status` for scope, artifacts, and
secrets.
