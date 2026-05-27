# Fork Quirks

This checkout tracks two remotes:

- `origin` is Key's fork: `kdmarble/hermes-agent`
- `upstream` is the source project: `NousResearch/hermes-agent`

`main` intentionally merges `upstream/main` and keeps local fork-only patches on
top. Do not reset or rebase those commits away during routine upstream catch-up
work.

## K10: Signal Tool Progress Fallback

Signal does not support editing previously sent messages. The fork keeps a
gateway progress fallback that sends each tool-call progress line as its own
message when the platform adapter reports `SUPPORTS_MESSAGE_EDITING = False`.

Code:

- `gateway/run.py`
- `gateway/platforms/signal.py`

Regression test:

- `tests/gateway/test_run_progress_topics.py::test_run_agent_non_editing_signal_sends_tool_progress_without_edits`

Merge checklist:

1. Preserve `SUPPORTS_MESSAGE_EDITING` checks in the gateway progress sender.
2. Preserve the send-only branch labeled `Editing unsupported: send just this line`.
3. Run the Signal progress regression test after merging `upstream/main`.
