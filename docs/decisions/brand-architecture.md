# Brand Architecture Decision

**Date:** 2026-04-19  
**Status:** Accepted

---

## Context

As Kusse Studio develops both a reusable template product (Kusse Folio) and a
client-facing managed website service (Handoff Studio), there is a risk of
conflating the two — treating them as one project, merging their repos, or
applying inconsistent naming. This decision clarifies the hierarchy and keeps
each thing doing one job.

---

## Decision

Maintain three distinct layers under the Kusse umbrella. Do not merge or rename
repos yet. Do not let operational momentum blur the purpose of each layer.

---

## Brand hierarchy

```
Kusse
└── Handoff Studio          (service brand — client-facing)
└── Kusse Folio             (product brand — template engine)
    └── Client sites        (individual deployments, e.g. Jat21.com)
```

---

## What each brand means

**Kusse**
The long-term umbrella. Not necessarily client-facing in the near term — more
a holding identity for the studio, its products, and its services.

**Handoff Studio** (`handoffstudio.com`)
The commercial service brand. Client-facing sales and service website.
Positioned around managed website delivery: setup, deployment, documentation,
ongoing support, and clean technical handover. The name reflects what clients
actually get — a professional, documented handover rather than a black-box
hosting relationship.

Positioning shorthand:
> "Handoff Studio by Kusse"
> Managed websites for small businesses, consultants, and professionals.
> Built on a tested template system. Delivered with setup, deployment, and handover.

Or when the product connection is relevant:
> "Handoff Studio — powered by Kusse Folio"

**Kusse Folio** (`ksbk/kusse-folio`)
The reusable Django template product. Not inherently client-facing — it is the
technical engine that powers both Handoff Studio deliveries and any future
licensed/self-hosted deployments. Has its own release discipline, health gate,
changelog, and documentation.

**Client sites** (e.g. `jat21architect-sys/jat21`)
Individual configured deployments. Each is one instance of Kusse Folio, shaped
by admin settings and content — not by forked or modified template code. Client
sites are not products; they are configured deliveries.

---

## Repo implications

| Repo | Purpose | Merge? |
| --- | --- | --- |
| `ksbk/kusse-folio` | Reusable template product | No — keep separate |
| `handoffstudio.com` repo | Service/marketing website | No — keep separate |
| `jat21architect-sys/jat21` (and future client repos) | Individual client deployments | No — each stays its own repo |
| Private ops repo (optional, future) | Client infrastructure matrices, transition checklists, account records | Not yet — create when needed |

The codebases serve different purposes and have different release cadences.
Merging them would make each harder to maintain and reason about.

---

## What not to do

- Do not merge `handoffstudio.com` and `ksbk/kusse-folio` into one repo.
- Do not add Handoff Studio marketing copy or pricing pages to the Kusse Folio
  template codebase.
- Do not add client-specific code paths to `ksbk/kusse-folio` — clients are
  configured instances, not forks.
- Do not rename repos yet — the naming is clear enough for now and a rename
  should follow a deliberate decision, not operational momentum.
- Do not let "Kusse Folio" become a client-facing brand unless it is
  intentionally positioned as a licensed or self-hosted product offering.

---

## Near-term next steps

1. **Keep Kusse Folio as the product/template engine.** Maintain release
   discipline, changelog, and health gate. v1.4.2 is the current locked release.

2. **Keep Handoff Studio as the service brand and site.** The `handoffstudio.com`
   site is the sales and intake surface — not a template, not a client site.

3. **Use consistent positioning language** where the connection between brands
   is mentioned: "Handoff Studio by Kusse" or "Powered by Kusse Folio."

4. **Do not rename repos yet.** Current names are accurate. Rename only if a
   deliberate repositioning decision follows.

5. **Do not merge repos yet.** Each serves a distinct purpose.

6. **Later: update Handoff Studio copy** to explain the managed website service
   model clearly — what the client owns, what Handoff Studio manages, and what
   handover looks like.

7. **Later: link Kusse Folio as the underlying product** where relevant in
   Handoff Studio copy — as a trust signal and technical credibility marker, not
   as a technical product pitch to non-technical clients.
