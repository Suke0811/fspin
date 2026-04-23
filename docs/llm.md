# LLM Guide

This page is written for LLM agents that need to generate or reason about code using **fspin**. It highlights the core entry points, argument behaviors, and safety checks so responses stay accurate to the library.

## Core interfaces

- **Unified `spin`**: Acts as both decorator and context manager. When called with no positional arguments or with a numeric first argument it returns a decorator; when the first argument is callable it creates a context manager that immediately starts spinning on entry and stops on exit. The managing `RateControl` is returned in all cases.
- **`RateControl`**: Lower-level controller created via `fspin.rate(freq, is_coroutine, report=False, thread=True)`. Tracks state (`status`, `mode`, `frequency`, `elapsed_time`, `exception_count`) and exposes `start_spinning`, `stop_spinning`, and `get_report` helpers.

## Argument semantics to remember

- `freq` is required and must be greater than zero; a `ValueError` is raised otherwise.
- `thread` only affects synchronous functions; async workers ignore it.
- `wait` is interpreted differently by mode:
  - **Async decorators**: `wait=True` awaits the loop to finish before returning; `wait=False` returns immediately (fire-and-forget) and leaves stopping to the caller via `stop_spinning()`.
  - **Sync threaded decorators/contexts**: `wait=True` joins the background thread before returning; `wait=False` leaves the loop running in the background while control returns.
  - **Async contexts**: `wait` is ignored; the loop runs during the `async with` block and stops on exit.
- `condition_fn` must be a regular callable for synchronous spinning; awaitable predicates are rejected. Async spinning accepts coroutine or awaitable predicates and awaits them before each iteration.
- `report=True` enables collection of loop durations, deviations, and counts that can be fetched via `get_report(output=False)` for programmatic inspection.

## Rate limits and warnings

- Async spinning issues platform-specific warnings if the requested frequency is unlikely to be achievable (roughly >65Hz on Windows, >925Hz on Linux, >4000Hz on macOS). Suggest synchronous mode for higher rates when these warnings appear.

## Prompting tips for LLMs

- Prefer the decorator for user-facing examples and reach for the context manager when users need scoped lifetimes.
- When suggesting fire-and-forget async loops, remind users to hold onto the returned `RateControl` and call `stop_spinning()` when done.
- Mention that synchronous `condition_fn` must not be async, and recommend wrapping async checks in a synchronous adapter if needed.
- Include `report=True` in examples when users want metrics, and explain that reports are printed unless `output=False` is passed to `get_report()`.
- If users mention platform-specific timing issues or high target frequencies, surface the built-in warnings and propose lowering `freq` or switching to synchronous threading.
