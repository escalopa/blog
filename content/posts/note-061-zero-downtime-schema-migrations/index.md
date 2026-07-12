---
title: "Zero-Downtime Schema Migrations"
date: 2025-05-09
slug: "zero-downtime-schema-migrations"
summary: "Expand, migrate, verify, switch, and contract across independently deployed application versions."
categories: ["databases"]
tags: ['databases', 'data', 'performance']
series: ["Data Systems"]
weight: 1061
---

{{< lead >}}
Expand, migrate, verify, switch, and contract across independently deployed application versions.
{{< /lead >}}

Senior engineering is less about memorizing a named pattern and more about making
the system's promises explicit. **Zero-Downtime Schema Migrations** is a useful case because the happy
path is usually easy; the difficult part is preserving the promise during load,
timeouts, retries, deploys, and partial failure.

## Start with the invariant

The working invariant for this design is simple: expand, migrate, verify, switch, and contract across independently deployed application versions.
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

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100,
    version = version + 1
WHERE id = 42
  AND version = 7
  AND balance >= 100;

-- The application requires exactly one affected row.
COMMIT;
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

Expand, migrate, verify, switch, and contract across independently deployed application versions. The reusable habit is to state the invariant, enforce bounds at the
correct boundary, and verify behavior under failure before optimizing the happy
path.
