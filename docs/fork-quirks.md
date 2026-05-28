# Private Live Fork Quirks

This checkout is the private runtime path, not the clean public fork.

- Path: `/home/key/.hermes/hermes-agent`
- Branch: `private/live-main`
- `origin`: `NousResearch/hermes-agent` fetch remote, push disabled
- `fork`: `kdmarble/hermes-agent` fetch remote, push disabled

Use `/home/key/homelab/hermes-agent` for clean upstream contribution branches.
That checkout's `main` mirrors `upstream/main` and its `origin` is the public
`kdmarble/hermes-agent` fork.

## Update Flow

When catching this live checkout up to upstream:

```bash
cd /home/key/.hermes/hermes-agent
git status --short --branch
git fetch --prune origin
git fetch --prune fork
git branch "backup/private-live-before-upstream-merge-$(date +%Y%m%d-%H%M%S)" private/live-main
git switch private/live-main
git merge --no-edit origin/main
```

Resolve conflicts by keeping upstream structure and re-laying the private
behavior below. Do not accept whole conflict files with `--ours` or `--theirs`
for the known patch paths.

## Private Patch Groups

### Signal Tool Progress Visibility

Signal does not support editing previously sent messages. The live fork keeps a
gateway progress fallback that sends each tool-call progress line as its own
message when the platform adapter reports `SUPPORTS_MESSAGE_EDITING = False`.

Files:

- `gateway/run.py`
- `gateway/platforms/signal.py`
- `tests/gateway/test_run_progress_topics.py`

Markers:

- `SUPPORTS_MESSAGE_EDITING = False`
- `_send_or_update_status_coro`
- `Editing unsupported: send just this line`
- `test_run_agent_non_editing_signal_sends_tool_progress_without_edits`

### Sender-To-Profile Routing

Signal senders can route to profile-specific `HERMES_HOME` state without
mutating process-wide environment.

Files:

- `gateway/run.py`
- `hermes_constants.py`
- `hermes_cli/profiles.py`

Markers:

- `_resolve_sender_profile`
- `SENDER_ROUTING`
- `_sender_hermes_home`
- `ContextVar`

Preserve the `ContextVar` approach during conflicts.

### Background Review Runtime Routing

`background_review` config can select provider, model, runtime, and iteration
limits independently of the parent session.

Files:

- `agent/background_review.py`
- `tests/run_agent/test_background_review.py`
- `tests/run_agent/test_background_review_toolset_restriction.py`

Markers:

- `background_review`
- `_configured_runtime`
- `resolve_runtime_provider`

### Hindsight Local Embedded Containment

The private runtime pins the local Hindsight client/runtime and can force
local embeddings and reranking to CPU to avoid stealing GPU memory from
inference.

Files:

- `plugins/memory/hindsight/__init__.py`
- `plugins/memory/hindsight/plugin.yaml`
- `plugins/memory/hindsight/README.md`
- `pyproject.toml`
- `uv.lock`

Markers:

- `_PINNED_CLIENT_VERSION`
- `_PINNED_LOCAL_VERSION`
- `HINDSIGHT_API_EMBEDDINGS_LOCAL_FORCE_CPU`
- `HINDSIGHT_API_RERANKER_LOCAL_FORCE_CPU`

### Personal-Context Memory Shim

The in-tree provider shim delegates to the homelab-private implementation.
Keep it out of public upstream branches unless a sanitized replacement is
explicitly requested.

Files:

- `plugins/memory/personal-context/__init__.py`
- `plugins/memory/personal-context/plugin.yaml`

Marker:

- `/home/key/homelab/hermes-plugins/personal-context`

### Other Local Behavior

- `tools/kanban_tools.py`: `_try_auto_subscribe` for kanban task notification
  subscription after natural-language task creation.
- `hermes_cli/kanban_specify.py`: auxiliary triage `extra_body`,
  `reasoning_content`, and bounded triage `max_tokens`.
- `tools/delegate_tool.py`: endpoint-aware credential pool guard via
  `_normalize_credential_pool_base_url` and `effective_base_url`.
- `tui_gateway/server.py`: `_mirror_browser_side_effects` and `BROWSER_CDP_URL`
  mirroring for `/browser connect` and `/browser disconnect`.
- `gateway/platforms/signal.py`: native Signal voice-note conversion with
  fallback to normal audio attachments.

## Targeted Validation

Run the tests for the paths touched by the merge. Default set:

```bash
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/gateway/test_run_progress_topics.py
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/gateway/test_signal.py
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/run_agent/test_background_review.py
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/tools/test_delegate.py
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/test_tui_gateway_server.py
HERMES_HOME="$(mktemp -d)" scripts/run_tests.sh tests/plugins/memory/test_hindsight_provider.py
```

Restart real services only after tests:

```bash
systemctl --user restart hermes-gateway.service hermes-web.service
systemctl --user status --no-pager hermes-gateway.service hermes-web.service
```
