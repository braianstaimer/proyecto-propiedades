---
name: design-patterns
description: Audit and apply proven design patterns (GoF Creational/Structural/Behavioral + modern TS/Python idioms). Use when reviewing architectures, refactoring for maintainability, or evaluating whether code would benefit from a specific pattern. Complements `architecture-patterns` (which focuses on macro-level Clean/Hexagonal/DDD).
user_invocable: true
---

# Design Patterns Audit & Apply

Systematic review of code (or a plan/design) to identify where a concrete design pattern would simplify, clarify, or future-proof the solution. Also detects misapplied or over-engineered pattern usage.

## When to invoke

- Reviewing an architectural plan/design doc.
- Pre-merge audit of a new feature involving polymorphism, conditional dispatch, or complex flow.
- Refactoring code with long if/elif chains, deep nesting, or tightly coupled logic.
- Evaluating whether a design decision (middleware chain, registry, lifecycle) should use a named pattern for clarity.

## Catalog (GoF + modern)

### Creational

| Pattern | Use when | Anti-signal |
|---|---|---|
| **Factory Method** | Subclasses decide which concrete class to instantiate | Only 1 concrete class |
| **Abstract Factory** | Families of related objects (e.g., `Theme → Button, Card, Input`) | Single product type |
| **Builder** | Object with many optional fields or complex init steps | 2-3 args fit in constructor |
| **Prototype** | Clone configured instances (e.g., default `DashboardConfig` → variants) | Plain copy works |
| **Singleton** | True process-global (logger, settings). Risky for testing | Anything needing mocking |

### Structural

| Pattern | Use when | Anti-signal |
|---|---|---|
| **Adapter** | Bridge incompatible interfaces (legacy API ↔ new domain) | Both interfaces identical |
| **Bridge** | Decouple abstraction from implementation (drivers, providers) | Single implementation |
| **Composite** | Tree structures processed uniformly (menus, permissions) | Flat list |
| **Decorator** | Dynamically add behavior (logging, caching, rate limit) | Static inheritance simpler |
| **Facade** | Hide complex subsystem behind simple interface (bootstrap, checkout) | Single-call subsystem |
| **Flyweight** | Many objects share state (icons, i18n bundles) | Few instances |
| **Proxy** | Intercept access (caching, lazy load, access control, ETag) | Direct access is fine |

### Behavioral

| Pattern | Use when | Anti-signal |
|---|---|---|
| **Chain of Responsibility** | Request passes through ordered handlers (middleware, config lookup chain) | Single handler |
| **Command** | Actions as first-class objects (undo, audit, queue) | Simple sync call |
| **Iterator** | Expose traversal without leaking structure | Built-in iteration |
| **Mediator** | Decouple N-way component talk (complex forms, chat) | 1-to-1 |
| **Memento** | Capture/restore state (undo, config snapshots) | No rewind needed |
| **Observer** | 1-to-N event notification (audit log, cache invalidation) | Single listener |
| **State** | Object behavior changes with state (token lifecycle, wizard steps) | Simple enum |
| **Strategy** | Pick algorithm at runtime (auth provider, email provider, preset theme) | Single algorithm |
| **Template Method** | Shared skeleton, overridable steps (ScopedRepository base) | No variation |
| **Visitor** | Operation over heterogeneous tree (AST walkers, report generators) | Homogeneous structure |

### Modern idioms (TS/Python context)

| Idiom | Use when |
|---|---|
| **Specification** | Composable business rules (CASL abilities, filters) |
| **Repository** | Abstract data access per aggregate (ScopedRepository) |
| **Registry** | Lookup by key with lazy load (module registry, plugin system) |
| **Dispatch map** | Replace `if/elif` chains with `{key: handler}` dict |
| **Guard clauses** | Replace nested `if` with early returns (see `no-nested-code`) |
| **Provider (React)** | Context + state + actions as composable hierarchy |
| **Hook (React)** | Encapsulate stateful behavior per concern |

## Audit process

When invoked on a plan or codebase:

### 1. Identify pattern opportunities

Scan for these signals:

| Signal | Likely pattern |
|---|---|
| Long `if/elif` chain over a type/string | **Strategy** or **Dispatch map** |
| Sequential side effects on single mutation | **Observer** (emit events) |
| Multi-step orchestration exposed to callers | **Facade** |
| Object state transitions with guards | **State machine** |
| Cross-cutting concern applied to many ops | **Decorator** |
| Tree traversal with uniform ops | **Composite** |
| Multiple impls selected at runtime | **Strategy** (+ factory to get it) |
| Lazy-loaded resources by key | **Registry** |
| Request passing through N processors | **Chain of Responsibility** |
| Base + variants sharing skeleton | **Template Method** |
| Incompatible external interface | **Adapter** |
| Access control / caching / lazy load wrapping | **Proxy** |

### 2. Evaluate fit

For each candidate, score honestly:

- **Necessity**: does this pattern solve a concrete pain (readability, testability, extensibility) or is it speculative?
- **Cost**: how much indirection does it add? (Interfaces, new types, runtime dispatch.)
- **Alternatives**: would a simple function, early return, or dispatch dict solve it with less ceremony?

**Rule:** apply a pattern only when (a) there are ≥2 current variants OR (b) there's a concrete upcoming variant in the plan. Never "just in case".

### 3. Flag anti-patterns

Report these explicitly:

- **God object / Facade over nothing**: Facade with a single underlying call.
- **Strategy with one strategy**: speculative; replace with direct call.
- **Observer without subscribers**: overkill; inline the side effect.
- **Abstract Factory for 1 product family**: use direct instantiation.
- **Singleton for testable state**: use DI instead.
- **Deep inheritance (> 2 levels)**: prefer composition.
- **Pattern soup**: 4+ patterns stacked on a simple flow.

### 4. Produce actionable report

Format:

```markdown
## Design Patterns Audit

### Applied correctly (keep)
- **[Pattern name]** — `src/path/file.ts:42` — why it's well-applied

### Recommended to apply
- **[Pattern name]** — for `[component/flow]`
  - Current: [how it is now, the pain]
  - Proposed: [pattern application, 3-5 line sketch]
  - Benefit: [testability / extensibility / readability]
  - Cost: [new types / indirection level]

### Anti-patterns detected
- **[Anti-pattern]** — `src/path/file.ts:10` — why and what to do

### Explicitly rejected (too speculative)
- Considered **[Pattern]** for `[X]` but rejected: only 1 variant exists, no upcoming variants. Direct call is simpler.
```

## Integration with other skills

- **`no-nested-code`**: deep nesting often resolves via Strategy, State, or Dispatch map.
- **`architecture-patterns`**: macro (Clean/Hexagonal/DDD). `design-patterns` is micro-level within those.
- **`/code-review`**: invoke on PRs touching multiple handlers, middleware chains, factories, or state machines.
- **`feature-audit`**: run after feature design to check pattern fitness before implementation.

## Output discipline

- **Reject speculative patterns.** "Might use this later" ≠ reason to introduce indirection now.
- **Quote code locations** (file:line) for both current state and proposed refactor.
- **Sketch the pattern application in ≤10 lines** — not full implementation.
- **Score severity**: `critical` (code is buggy/unsafe without it), `major` (clarity/testability suffers), `minor` (stylistic improvement).
- **No ceremony**: if a function + early returns solves it, don't propose a pattern.

## Common applications in this codebase's context

Already-present patterns (preserved and extended):
- **Template Method**: `ScopedRepository[T]` base with overridable per-model queries.
- **Chain of Responsibility**: `ConfigProvider` (App.config → PlatformSettings → default).
- **Singleton**: `settings` object.
- **Decorator**: `@limiter.limit(CONST)`, `@router.get(...)`.
- **Provider**: React `ConfigContext`, `AuthContext`, `AbilityContext`.
- **Repository**: per-domain Beanie repos.

Opportunities frequently worth evaluating:
- **Strategy** for future auth methods (OAuth, SSO on top of magic link).
- **Strategy** for email providers (SMTP/SES/Postmark).
- **Facade** for bootstrap orchestration (auth token + config + i18n + error handling).
- **Observer** for config mutations (audit + CDN invalidate + CORS refresh).
- **State machine** for `MagicLinkToken` lifecycle.
- **Builder** for complex theme or config creation when > 5 fields chain.
- **Registry + Factory** for dynamic module resolution.
- **Proxy** for ETag-aware config fetches.
- **Specification** for composable CASL abilities.
