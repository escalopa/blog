---
title: "Saga Coordination Without Mystery"
date: 2025-02-25
slug: "saga-coordination-without-mystery"
summary: "A saga is a state machine of forward actions, durable decisions, and explicit compensations."
categories: ["distributed-systems"]
tags: ['distributed-systems', 'reliability', 'system-design']
series: ["Distributed Systems"]
weight: 1032
---

{{< lead >}}
A saga is a state machine of forward actions, durable decisions, and explicit compensations.
{{< /lead >}}

Senior engineering is less about memorizing a named pattern and more about making
the system's promises explicit. **Saga Coordination Without Mystery** is a useful case because the happy
path is usually easy; the difficult part is preserving the promise during load,
timeouts, retries, deploys, and partial failure.

## Start with the invariant

The working invariant for this design is simple: a saga is a state machine of forward actions, durable decisions, and explicit compensations.
Write that sentence next to the design. It gives reviewers something falsifiable
and prevents the implementation from becoming a collection of unrelated knobs.

Before choosing a library or service, answer four questions:

1. What user-visible outcome must remain true?
2. Which component owns the decision and its durable state?
3. What are the time, memory, queue, and retry bounds?
4. How will an operator distinguish healthy degradation from data loss?

If any answer is "unbounded" or "we will inspect logs," the design is not ready.

## A compact implementation sketch

The following example is deliberately small. It demonstrates the boundary and
the failure shape; production code should add domain-specific validation,
metrics, tests, and dependency policy.

```go
func retry(ctx context.Context, max int, call func(context.Context) error) error {
    delay := 20 * time.Millisecond
    for attempt := 0; attempt < max; attempt++ {
        if err := call(ctx); err == nil { return nil }
        jitter := time.Duration(rand.Int64N(int64(delay / 2)))
        select {
        case <-time.After(delay + jitter):
            delay = min(delay*2, time.Second)
        case <-ctx.Done():
            return ctx.Err()
        }
    }
    return errors.New("retry budget exhausted")
}
```

The important detail is not the syntax. The example keeps policy near the
boundary where the system can enforce it. That makes overload and failure
observable instead of allowing them to surface later as random latency.

## Failure modes worth designing first

- **Duplicate work:** a timeout does not prove the remote side did nothing.
- **Queue growth:** accepting work faster than dependencies finish converts a
  capacity problem into a memory and tail-latency problem.
- **Ambiguous ownership:** two components that can both decide truth create a
  reconciliation problem, even when the normal path appears correct.
- **Coordinated recovery:** identical clients retrying on identical schedules
  can keep a recovered dependency overloaded.
- **Invisible degradation:** success rate alone can hide stale, partial, or
  excessively slow results.

These failures are connected. For example, a slow dependency consumes the
deadline, triggers a retry, doubles work, fills a queue, and finally causes an
unrelated endpoint to miss its SLO. A useful design review follows that chain
rather than reviewing each mechanism in isolation.

## Production checklist

- Put a deadline on every remote or blocking boundary.
- Bound concurrency and queued work independently.
- Define which failures are safe to retry and which are permanent.
- Make repeated commands safe, or make duplicate effects detectable.
- Emit low-cardinality metrics for attempts, outcomes, latency, and saturation.
- Test cancellation, partial completion, dependency slowness, and process restart.
- Document the rollout signal and the fastest safe rollback.

## How I would validate it

Start with a deterministic unit test for the invariant. Add an integration test
that stops the dependency after it accepts work but before it replies. Then run a
load test that exceeds planned capacity gradually. Watch the latency distribution,
queue depth, in-flight work, dependency errors, and recovery time—not only average
throughput.

Finally, inject one failure at a time: latency, connection refusal, malformed
data, duplicate delivery, and restart. The system should either preserve its
promise or fail in the documented way. That is the difference between code that
works in a demo and a service that can be operated.

## Takeaway

A saga is a state machine of forward actions, durable decisions, and explicit compensations. The reusable habit is to state the invariant, enforce bounds at the
correct boundary, and verify behavior under failure before optimizing the happy
path.
