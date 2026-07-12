#!/usr/bin/env python3
"""Generate the resume-aligned engineering notes published by this site.

The catalog is intentionally data-driven: adding a note requires a title and a
specific engineering claim, while the renderer keeps structure and visuals
consistent. Generated files live under content/posts/ and are safe to rebuild.
"""

from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "posts"
PUBLISHED = "2026-07-11"

# series, category, title, core claim
CATALOG = [
    # Go in production
    ("Production Go", "go", "Designing Bounded Worker Pools in Go", "Bound concurrency at the admission point so overload becomes visible and controllable."),
    ("Production Go", "go", "Cancellation That Actually Propagates in Go", "A context is useful only when every blocking boundary observes it and cleanup has a clear owner."),
    ("Production Go", "go", "Error Chains You Can Operate in Go", "Wrap errors for diagnosis, classify them for policy, and never make callers parse prose."),
    ("Production Go", "go", "Graceful Shutdown Without Dropping Requests", "Shutdown is a protocol: stop admission, drain in-flight work, flush state, then release dependencies."),
    ("Production Go", "go", "Choosing Pointers and Values in Go APIs", "Choose receiver and parameter semantics from ownership, mutability, and copy cost rather than habit."),
    ("Production Go", "go", "Making Go HTTP Clients Production Ready", "Timeouts, connection reuse, response draining, and retry policy belong in the client design."),
    ("Production Go", "go", "Table-Driven Tests That Stay Readable", "A good table captures behavior dimensions without hiding the arrange-act-assert story."),
    ("Production Go", "go", "Race-Free In-Memory Caches in Go", "Correct cache synchronization must cover compound operations, expiry, and loader duplication."),
    ("Production Go", "go", "When Channels Are the Wrong Abstraction", "Use channels for ownership transfer and coordination, not as a universal replacement for locks."),
    ("Production Go", "go", "Building Backpressure Into Go Pipelines", "A pipeline without bounded queues and cancellation is an outage amplifier."),
    ("Production Go", "go", "Profiling Go Services With pprof", "Profile the constrained resource under representative load before changing code."),
    ("Production Go", "go", "Reducing Allocations in Hot Go Paths", "Allocation work starts with profiles and escape analysis, then targets lifetime and representation."),
    ("Production Go", "go", "Safe Configuration Loading in Go", "Parse once, validate completely, expose immutable typed configuration, and fail before serving traffic."),
    ("Production Go", "go", "Functional Options Without API Confusion", "Options help optional construction only when defaults, validation, and option interaction remain obvious."),
    ("Production Go", "go", "Interfaces at the Point of Use", "Small consumer-owned interfaces reduce coupling and make tests describe real dependencies."),
    ("Production Go", "go", "Structured Concurrency Patterns in Go", "Child goroutines should share cancellation, error propagation, and a bounded lifetime with their parent."),
    ("Production Go", "go", "Avoiding Goroutine Leaks", "Every goroutine needs an exit condition that remains reachable when downstream work stops."),
    ("Production Go", "go", "Benchmarking Go Code Without Lying to Yourself", "Benchmarks need stable inputs, allocation reporting, multiple runs, and a comparison tied to user impact."),
    ("Production Go", "go", "Designing Stable Go Packages", "A package is stable when its responsibilities, exported surface, and dependency direction are narrow."),
    ("Production Go", "go", "Building a Generic TTL Cache in Go", "Generics can remove unsafe casts while explicit synchronization and expiry semantics preserve correctness."),

    # Distributed systems
    ("Distributed Systems", "distributed-systems", "Raft Leader Election From First Principles", "Randomized election timeouts and term monotonicity turn competing candidates into one current leader."),
    ("Distributed Systems", "distributed-systems", "Log Replication and the Raft Safety Story", "A leader commits only entries known to be durable on a quorum, preserving one ordered history."),
    ("Distributed Systems", "distributed-systems", "Designing Idempotent Consumers", "Persist the business effect and message identity in one atomic boundary whenever possible."),
    ("Distributed Systems", "distributed-systems", "Exactly Once Is Usually a Local Property", "End-to-end exactly-once claims decompose into deduplication, atomicity, and replay-safe effects."),
    ("Distributed Systems", "distributed-systems", "Retries, Timeouts, and the Latency Budget", "Retries spend remaining deadline and capacity; they do not create either."),
    ("Distributed Systems", "distributed-systems", "Exponential Backoff With Jitter", "Jitter breaks synchronized retry waves while caps and deadlines bound recovery cost."),
    ("Distributed Systems", "distributed-systems", "Circuit Breakers Are Not Error Handling", "A breaker protects a dependency and caller capacity; ordinary failures still require explicit policy."),
    ("Distributed Systems", "distributed-systems", "Consistent Hashing for Practical Sharding", "A hash ring limits key movement, but load balance still depends on virtual nodes and key distribution."),
    ("Distributed Systems", "distributed-systems", "Quorums Without the Hand Waving", "Intersecting read and write quorums provide a reasoning tool, not automatic availability or freshness."),
    ("Distributed Systems", "distributed-systems", "Ordering Events in Distributed Systems", "Choose the weakest ordering guarantee the business invariant needs and encode it per entity."),
    ("Distributed Systems", "distributed-systems", "Outbox Pattern for Reliable Event Publishing", "Commit state and an event record together, then publish asynchronously with idempotent delivery."),
    ("Distributed Systems", "distributed-systems", "Saga Coordination Without Mystery", "A saga is a state machine of forward actions, durable decisions, and explicit compensations."),
    ("Distributed Systems", "distributed-systems", "Lease-Based Distributed Locks", "A lease bounds stale ownership only when fencing tokens protect the resource from expired holders."),
    ("Distributed Systems", "distributed-systems", "Read Repair and Anti-Entropy", "Foreground repair improves observed keys while background comparison closes the long tail."),
    ("Distributed Systems", "distributed-systems", "Handling Hot Keys Before They Melt a Service", "Detect skew, isolate the key, coalesce work, and change partitioning only with evidence."),
    ("Distributed Systems", "distributed-systems", "Load Shedding as a Correctness Feature", "Rejecting excess work early preserves useful throughput and bounded latency for admitted requests."),
    ("Distributed Systems", "distributed-systems", "Designing for Partial Failure", "Timeout, retry, fallback, and reconciliation paths are first-class behavior, not exceptional code."),
    ("Distributed Systems", "distributed-systems", "Version Vectors in Plain Language", "Version vectors distinguish causality from concurrency when one scalar version cannot."),
    ("Distributed Systems", "distributed-systems", "Gossip Protocols and Eventual Membership", "Random peer exchange trades immediate agreement for scalable, failure-tolerant convergence."),
    ("Distributed Systems", "distributed-systems", "A Practical Failure Detector", "Failure detectors produce suspicions from imperfect timing; the application decides how costly suspicion may be."),

    # APIs and integration
    ("Backend APIs", "backend", "Designing Evolvable REST APIs", "Compatibility comes from additive change, explicit semantics, and a deprecation path clients can observe."),
    ("Backend APIs", "backend", "gRPC Deadlines and Error Semantics", "Deadlines cross service boundaries; status codes must separate retryable transport conditions from domain outcomes."),
    ("Backend APIs", "backend", "OpenAPI as an Executable Contract", "Treat the schema as reviewed source code and test implementations and clients against it."),
    ("Backend APIs", "backend", "Cursor Pagination That Survives Concurrent Writes", "A cursor must encode a stable total ordering, not merely an offset into changing rows."),
    ("Backend APIs", "backend", "Idempotency Keys for Write APIs", "Bind a client key to request identity and persist the decided response for the retry window."),
    ("Backend APIs", "backend", "OAuth 2.0 Boundaries for Backend Engineers", "Validate issuer, audience, signature, expiry, and scopes at the resource boundary."),
    ("Backend APIs", "backend", "Webhooks That Can Be Retried Safely", "Sign payloads, preserve event identity, acknowledge quickly, and make processing replay-safe."),
    ("Backend APIs", "backend", "Rate Limiting With Token Buckets", "Token buckets express sustained rate and burst capacity while keeping admission decisions cheap."),
    ("Backend APIs", "backend", "Validating Requests Without Leaking Internals", "Separate syntactic validation, domain rules, and authorization, then return stable problem details."),
    ("Backend APIs", "backend", "API Versioning Without Permanent Forks", "Prefer compatible evolution; version only when semantics truly conflict and plan convergence."),
    ("Backend APIs", "backend", "Designing Batch Endpoints", "Batch APIs need per-item outcomes, bounded size, deterministic identity, and explicit atomicity."),
    ("Backend APIs", "backend", "Safe File Upload Pipelines", "Stream with hard limits, quarantine content, verify type independently, and decouple scanning from trust."),
    ("Backend APIs", "backend", "Integrating Unreliable Third-Party APIs", "Put timeouts, quotas, translation, idempotency, and observability behind an anti-corruption layer."),
    ("Backend APIs", "backend", "WebSockets With Bounded Resources", "Every connection needs limits for authentication, queues, heartbeats, fan-out, and shutdown."),
    ("Backend APIs", "backend", "GraphQL N Plus One and DataLoader", "Batching fixes duplicate fetch shape only when caching scope and authorization remain request-local."),

    # Data systems
    ("Data Systems", "databases", "PostgreSQL Indexes From Query Shape", "Design indexes from predicates, join keys, ordering, selectivity, and write cost together."),
    ("Data Systems", "databases", "Reading EXPLAIN ANALYZE Without Guessing", "Compare estimated and actual rows first, then find where time, loops, or memory multiply."),
    ("Data Systems", "databases", "Transaction Isolation Through Anomalies", "Choose isolation by naming the anomaly that would violate a business invariant."),
    ("Data Systems", "databases", "The Lost Update and How to Prevent It", "Atomic updates, locks, or optimistic versions must protect read-modify-write as one decision."),
    ("Data Systems", "databases", "Keyset Pagination in PostgreSQL", "Seek from the last ordered key to keep page cost stable and results coherent."),
    ("Data Systems", "databases", "Zero-Downtime Schema Migrations", "Expand, migrate, verify, switch, and contract across independently deployed application versions."),
    ("Data Systems", "databases", "Redis Caching Without Stale Data Surprises", "Define ownership, expiry, invalidation, stampede control, and degraded behavior before adding cache code."),
    ("Data Systems", "databases", "Cache Stampede Protection", "Request coalescing, early refresh, and jitter keep one expiry from becoming a dependency spike."),
    ("Data Systems", "databases", "Kafka Partitioning and Consumer Parallelism", "The key determines ordering and skew; partition count sets the ceiling for group parallelism."),
    ("Data Systems", "databases", "Kafka Delivery Semantics in Practice", "Offsets and side effects must share a recoverable protocol to survive crashes between them."),
    ("Data Systems", "databases", "ClickHouse Table Design for Event Analytics", "Partition for lifecycle, order for filtering locality, and measure cardinality before choosing codecs."),
    ("Data Systems", "databases", "ETCD Transactions for Coordination", "Compare-and-swap plus leases can encode ownership, but clients must handle revision and expiry races."),
    ("Data Systems", "databases", "PostGIS Nearest-Neighbor Queries", "Use spatial indexes and distance operators that preserve indexability before calculating exact distance."),
    ("Data Systems", "databases", "Connection Pools Are Capacity Limits", "Pool size must reflect database concurrency, transaction duration, and queueing—not application goroutine count."),
    ("Data Systems", "databases", "Choosing Between Redis and Memcached", "Choose from data model, persistence, operations, clustering, and failure behavior rather than benchmark headlines."),

    # Reliability and platform
    ("Reliable Platforms", "platform", "Defining SLOs Engineers Can Use", "An SLO connects user-visible success to an error budget and concrete release decisions."),
    ("Reliable Platforms", "platform", "Prometheus Metrics That Survive Production", "Instrument bounded dimensions and user outcomes; labels are a data model with a capacity cost."),
    ("Reliable Platforms", "platform", "Histograms and Tail Latency", "Choose buckets around decisions and inspect distributions; averages conceal the users waiting longest."),
    ("Reliable Platforms", "platform", "Tracing Across gRPC Services", "Propagate context, name spans by operation, and attach identifiers without recording sensitive payloads."),
    ("Reliable Platforms", "platform", "OpenTelemetry Without Vendor Lock-In", "Keep instrumentation semantic and portable while isolating exporter and sampling policy."),
    ("Reliable Platforms", "platform", "Structured Logging That Helps During Incidents", "Logs need stable event names, correlation, severity discipline, and deliberate data minimization."),
    ("Reliable Platforms", "platform", "Kubernetes Probes Done Right", "Startup, readiness, and liveness answer different questions and should trigger different actions."),
    ("Reliable Platforms", "platform", "Kubernetes Resource Requests and Limits", "Requests drive placement; limits change runtime behavior; both need measurements from realistic load."),
    ("Reliable Platforms", "platform", "Safe Deployments With Readiness Gates", "A rollout is safe when new instances prove dependencies, warmup, and service health before receiving load."),
    ("Reliable Platforms", "platform", "Secrets Management With Vault", "Use short-lived identity-bound credentials and design renewal and revocation as runtime paths."),
    ("Reliable Platforms", "platform", "Docker Images for Go Services", "A reproducible multi-stage build and minimal runtime reduce drift, size, and attack surface."),
    ("Reliable Platforms", "platform", "NGINX Timeouts Across a Proxy Chain", "Align connect, header, body, idle, and upstream deadlines so one layer does not outlive another."),
    ("Reliable Platforms", "platform", "Incident Response From Symptom to Evidence", "Stabilize impact, preserve a timeline, test hypotheses with signals, and separate recovery from diagnosis."),
    ("Reliable Platforms", "platform", "Capacity Planning With Little's Law", "Concurrency equals arrival rate times time in system, giving a fast check for queues and resource demand."),
    ("Reliable Platforms", "platform", "Designing Useful Grafana Dashboards", "Start from operator questions and put traffic, errors, latency, saturation, and deploy context together."),

    # Architecture and engineering leadership
    ("Architecture Practice", "architecture", "Writing Architecture Decision Records", "Record context, forces, decision, consequences, and revisit triggers while the reasoning is fresh."),
    ("Architecture Practice", "architecture", "Modular Monolith Before Microservices", "Strong internal boundaries earn optional distribution without paying network and operations costs early."),
    ("Architecture Practice", "architecture", "Finding Service Boundaries With Invariants", "Place data and behavior that change under one invariant behind the same consistency boundary."),
    ("Architecture Practice", "architecture", "The Real Cost of a Microservice", "Each service adds deployment, ownership, observability, compatibility, and failure-management obligations."),
    ("Architecture Practice", "architecture", "Hexagonal Architecture in Practical Go", "Keep domain decisions behind ports and push transport and storage details to adapters."),
    ("Architecture Practice", "architecture", "Evolutionary Architecture With Fitness Functions", "Automate checks for the architectural properties that must remain true as teams and systems change."),
    ("Architecture Practice", "architecture", "Design Reviews That Produce Decisions", "Share constraints and alternatives early, assign decision ownership, and record unresolved risks."),
    ("Architecture Practice", "architecture", "Turning Product Requirements Into System Constraints", "Translate user journeys into load, latency, consistency, privacy, availability, and cost envelopes."),
    ("Architecture Practice", "architecture", "Planning a Safe Service Rollout", "Stage exposure, define observability and rollback signals, and test compatibility before scaling traffic."),
    ("Architecture Practice", "architecture", "Cross-Team API Ownership", "One team owns the contract while consumers participate through compatibility tests and change visibility."),
    ("Architecture Practice", "architecture", "Technical Onboarding as a System", "Give newcomers a map, a runnable path, progressive tasks, and feedback loops instead of a document dump."),
    ("Architecture Practice", "architecture", "Teaching Distributed Systems With Failure Scenarios", "Start from observable failures and invariants, then introduce algorithms as tools that preserve them."),
    ("Architecture Practice", "architecture", "Code Review for High-Load Services", "Review correctness under concurrency, bounds, failure behavior, observability, and rollout—not only syntax."),
    ("Architecture Practice", "architecture", "Performance Optimization as an Experiment", "State a measurable hypothesis, control the workload, compare distributions, and retain a rollback path."),
    ("Architecture Practice", "architecture", "Building a Latency Budget Across Services", "Allocate a percentile-aware deadline across work, dependencies, queues, and limited retries."),
]


PALETTES = {
    "go": ("#071a2b", "#00add8", "GO"),
    "distributed-systems": ("#15122b", "#8b5cf6", "DS"),
    "backend": ("#08261f", "#34d399", "API"),
    "databases": ("#25160a", "#f59e0b", "DB"),
    "platform": ("#260d19", "#fb7185", "OPS"),
    "architecture": ("#111827", "#60a5fa", "ARC"),
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def code_example(category: str, title: str) -> tuple[str, str]:
    if category == "go":
        return "go", '''ctx, cancel := context.WithTimeout(context.Background(), 800*time.Millisecond)
defer cancel()

result := make(chan error, 1)
go func() { result <- doWork(ctx) }()

select {
case err := <-result:
    return err
case <-ctx.Done():
    return fmt.Errorf("work deadline: %w", ctx.Err())
}'''
    if category == "distributed-systems":
        return "go", '''func retry(ctx context.Context, max int, call func(context.Context) error) error {
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
}'''
    if category == "backend":
        return "go", '''type Problem struct {
    Type   string `json:"type"`
    Title  string `json:"title"`
    Status int    `json:"status"`
    Trace  string `json:"trace_id,omitempty"`
}

func writeProblem(w http.ResponseWriter, status int, title string) {
    w.Header().Set("Content-Type", "application/problem+json")
    w.WriteHeader(status)
    _ = json.NewEncoder(w).Encode(Problem{
        Type: "about:blank", Title: title, Status: status,
    })
}'''
    if category == "databases":
        return "sql", '''BEGIN;

UPDATE accounts
SET balance = balance - 100,
    version = version + 1
WHERE id = 42
  AND version = 7
  AND balance >= 100;

-- The application requires exactly one affected row.
COMMIT;'''
    if category == "platform":
        return "yaml", '''startupProbe:
  httpGet: { path: /health/startup, port: 8080 }
  failureThreshold: 30
  periodSeconds: 2
readinessProbe:
  httpGet: { path: /health/ready, port: 8080 }
  periodSeconds: 5
livenessProbe:
  httpGet: { path: /health/live, port: 8080 }
  periodSeconds: 10'''
    return "text", '''Context:       What changed, and which constraint matters?
Options:       What are the credible alternatives?
Decision:      Who decides, and what was selected?
Consequences:  What becomes easier or harder?
Signals:       How will we know the decision is wrong?
Revisit:       Which event should reopen this decision?'''


def article(series: str, category: str, title: str, claim: str, index: int) -> str:
    slug = slugify(title)
    language, snippet = code_example(category, title)
    tags = {
        "go": ["go", "concurrency", "performance"],
        "distributed-systems": ["distributed-systems", "reliability", "system-design"],
        "backend": ["api-design", "backend", "integration"],
        "databases": ["databases", "data", "performance"],
        "platform": ["observability", "kubernetes", "reliability"],
        "architecture": ["architecture", "engineering-leadership", "system-design"],
    }[category]
    return f'''---
title: "{title}"
date: {PUBLISHED}
slug: "{slug}"
summary: "{claim}"
categories: ["{category}"]
tags: {tags!r}
series: ["{series}"]
weight: {1000 + index}
---

{{{{< lead >}}}}
{claim}
{{{{< /lead >}}}}

Senior engineering is less about memorizing a named pattern and more about making
the system's promises explicit. **{title}** is a useful case because the happy
path is usually easy; the difficult part is preserving the promise during load,
timeouts, retries, deploys, and partial failure.

## Start with the invariant

The working invariant for this design is simple: {claim[0].lower() + claim[1:]}
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

```{language}
{snippet}
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

{claim} The reusable habit is to state the invariant, enforce bounds at the
correct boundary, and verify behavior under failure before optimizing the happy
path.
'''


def cover(title: str, category: str) -> str:
    bg, accent, mark = PALETTES[category]
    safe = html.escape(title)
    words = title.split()
    midpoint = max(1, len(words) // 2)
    line1 = html.escape(" ".join(words[:midpoint]))
    line2 = html.escape(" ".join(words[midpoint:]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="{safe}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="#020617"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#g)"/>
<circle cx="1060" cy="90" r="210" fill="{accent}" opacity=".12"/><circle cx="1040" cy="560" r="300" fill="{accent}" opacity=".08"/>
<path d="M80 128h160" stroke="{accent}" stroke-width="10"/><text x="80" y="105" fill="{accent}" font-family="ui-monospace,monospace" font-size="34" font-weight="700">ENGINEERING NOTE · {mark}</text>
<text x="80" y="285" fill="#f8fafc" font-family="Inter,Arial,sans-serif" font-size="58" font-weight="700"><tspan x="80">{line1}</tspan><tspan x="80" dy="76">{line2}</tspan></text>
<text x="80" y="560" fill="#94a3b8" font-family="Inter,Arial,sans-serif" font-size="28">Ahmed Helaly · escalopa.com</text>
</svg>'''


def main() -> None:
    if len(CATALOG) != 100:
        raise SystemExit(f"catalog must contain 100 entries, got {len(CATALOG)}")
    slugs: set[str] = set()
    for index, (series, category, title, claim) in enumerate(CATALOG, start=1):
        slug = slugify(title)
        if slug in slugs:
            raise SystemExit(f"duplicate slug: {slug}")
        slugs.add(slug)
        digest = hashlib.sha1(title.encode()).hexdigest()[:6]
        folder = POSTS / f"note-{index:03d}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.md").write_text(article(series, category, title, claim, index), encoding="utf-8")
        (folder / "featured.svg").write_text(cover(title, category), encoding="utf-8")
        (folder / ".generated").write_text(f"{digest}\n", encoding="ascii")

    print(f"generated {len(CATALOG)} engineering notes in {POSTS}")


if __name__ == "__main__":
    main()
