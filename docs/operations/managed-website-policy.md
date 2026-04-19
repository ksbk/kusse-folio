# Managed Website Service — Operational Policy

**Applies to:** Kusse Studio client website engagements  
**Scope:** Non-technical clients receiving managed hosting and ongoing support

---

## Purpose

This document defines the default operating model for Kusse Studio managed
website services. It clarifies what the studio manages, what the client owns,
and how account access and handover rights are structured.

---

## Default model for non-technical clients

Kusse Studio manages all technical infrastructure. The client owns their domain,
brand, content, and business data. The client gets a named admin/editor account
for content management. Kusse Studio holds a separate named operator account.

This model is the default unless the client explicitly requests a self-managed
or co-managed arrangement and accepts the operational responsibilities that come
with it.

---

## What Kusse Studio manages

- **GitHub / repo workflow** — source code, releases, and deployment history
- **Hosting / deployment** — Railway (or equivalent), deployment configuration,
  release gating
- **Database operations** — provisioning, migrations, manual backups on request,
  monitoring for data integrity
- **Media / storage** — Cloudinary (or equivalent) account and credentials for
  uploaded images and files
- **Environment variables / secrets** — `SECRET_KEY`, API keys, SMTP credentials,
  Cloudinary credentials; rotated when needed, never shared in plaintext via
  email or chat
- **Updates / security patches** — template upgrades, dependency updates,
  Django security releases
- **Monitoring / troubleshooting** — error tracking (Sentry or equivalent),
  uptime checks, incident response

---

## What the client owns

- **Domain** — registrar account, DNS records, renewal responsibility
- **Brand assets** — logo files, typography, color specifications
- **Website content** — all copy, project images, descriptions, service
  listings, portfolio assets entered via admin
- **Customer / contact / business data** — enquiries, contact form submissions,
  any business records stored in the database
- **Admin / editor account** — a named Django admin account under the client's
  own email address, with the ability to add/edit/delete their own content
- **Export and handover rights** — see below

---

## Account model

- Each client has **one named admin/editor account** under their own email.
  This account is theirs. They can log in, manage content, and create
  additional editor accounts for their team.
- Kusse Studio holds **one named operator/admin account** under a studio email
  address. This is used for deployment support, troubleshooting, and updates.
  It is not the only recovery path.
- **No shared anonymous superuser** should be the only admin account.
- **No single person or account** should be the only recovery path. If the
  studio operator account were to be lost, the client's own account (or another
  documented admin) must still have full access.
- Credentials are never shared in plaintext via email, Slack, or any other
  messaging platform. Use a password manager or secure handoff.

---

## Handover and export rights

If the client requests a handover or if the relationship ends:

- **Source code:** The git repository can be transferred to the client's GitHub
  account, forked to their control, or delivered as an archive.
- **Database export:** A full Postgres dump is provided. The client can restore
  this to any compatible Postgres host.
- **Media export:** All uploaded files are downloadable from Cloudinary or the
  equivalent media storage, either via the Cloudinary dashboard or a bulk export.
- **Environment variables:** A documented list of all required environment
  variables and their roles is provided (not the secret values — those must be
  rotated on handover; the list tells the recipient what they need to set up).
- **Deployment / DNS notes:** Current Railway service configuration and any
  DNS records required to keep the domain pointing at the site are documented.
- **Timeline:** Handover is initiated within 14 days of a written request unless
  otherwise agreed.

---

## What to avoid

- **Client-specific code paths in the shared template.** Any fix that is truly
  specific to one client belongs in their deployment configuration or admin
  settings, not in template code.
- **Undocumented accounts.** Every account used in a client deployment must be
  recorded in the client's infrastructure ownership matrix.
- **Credentials shared via email or chat.** Always use a password manager or
  secure handoff flow.
- **One person as the only admin.** Both the client and the studio must have
  independent admin access that does not depend on the other party.
- **Unclear domain/DNS ownership.** DNS control and registrar access must be
  confirmed and documented before launch and at every handover.

---

## Technical clients and co-managed arrangements

For technically capable clients who want to own their infrastructure, the
following applies:

- Client-owned Railway, GitHub, Cloudinary, and SMTP accounts are acceptable.
- If Kusse Studio provides ongoing support, the studio **must** be added as an
  admin or team member on each service. Read-only access is not sufficient for
  deployment support.
- The same account model applies: named studio operator account, named client
  admin account, no single recovery path.
- The infrastructure ownership matrix must be completed before support begins.
