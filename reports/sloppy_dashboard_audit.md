# ADSI Audit Report — ADSI Demo

**Screen:** Sloppy Dashboard  
**Auditor:** ADSI Engine v3 static scan  
**Date:** 2026-06-03  
**Rubric:** 3.0.0

## Score: 46.74/100 — high_slop

ADSI static audit scored 46.74/100 (high_slop). Highest-impact areas: A, B, G.

## Area Breakdown

| Area | Severity | Weighted | Key evidence | First fix |
|---|---:|---:|---|---|
| A Realisme Data & Domain | 5.0 | 15.0 | [mock-data] sloppy_dashboard.html:20 — Mock/demo/hardcoded data signal found in UI path. Evidence: Absen</p>         <p>Coming soon</p>       </div>       <script>         const mockData = [{ name: 'Jane Doe', status: 'pending' }]         console.log(mockData) | Move demo data behind fixtures and connect production UI to real data contracts. |
| B Kejelasan Workflow | 3.1 | 7.44 | [dead-href] sloppy_dashboard.html:9 — Dead link/CTA found. Evidence: le="background:#8b5cf6">         <p>Total active users increased</p>         <a href="#">Review</a>       </div>       <div class="card backdrop-blur bg-white/20 w-[720 | Replace dead href with a real route, disabled state explanation, or remove CTA. |
| C Konsistensi Design System | 1.4 | 3.36 | [inline-style] sloppy_dashboard.html:7 — Inline style found. Evidence: 1>       <h3>Active Users</h3>       <div class="card shadow-xl rounded-[19px]" style="background:#8b5cf6">         <p>Total active users increased</p>         <a href | Move styling to design-system primitives or tokens unless truly dynamic. |
| D Hirarki Informasi | 0.1 | 0.2 | [skipped-heading-risk] sloppy_dashboard.html:5 — Heading found; hierarchy will be checked globally. Evidence: adient-to-r from-purple-500 to-violet-500 text-transparent bg-clip-text">       <h1>Dashboard Overview</h1>       <h3>Active Users</h3>       <div class="card shad | Keep heading levels sequential and meaningful. |
| E Copywriting & Lokalisasi | 1.0 | 2.0 | [mixed-id-en] sloppy_dashboard.html:5 — English UI term found; check localization consistency. Evidence: nt-to-r from-purple-500 to-violet-500 text-transparent bg-clip-text">       <h1>Dashboard Overview</h1>       <h3>Active Users</h3>       <div class="card shadow-xl roun | Localize terms or document intentional product vocabulary. |
| F State & Status Logic | 2.6 | 5.2 | [status-taxonomy-sprawl] global — Many status labels detected; taxonomy may be inconsistent. Evidence: absen, active, aktif, belum, completed, ditinjau, error, hadir, pending, perlu, sudah | Create a status taxonomy table with dimensions, allowed values, and UI placement. |
| G Aksesibilitas | 2.8 | 5.6 | [img-alt-missing] sloppy_dashboard.html:12 — Image without alt attribute. Evidence: </div>       <div class="card backdrop-blur bg-white/20 w-[720px]">         <img src="/avatar.png">         <button><svg></svg></button>         <div onClick="d | Add meaningful alt text or alt="" for decorative images. |
| H Layout & Responsiveness | 1.3 | 2.08 | [fixed-px] sloppy_dashboard.html:11 — Fixed pixel dimension found. Evidence: ef="#">Review</a>       </div>       <div class="card backdrop-blur bg-white/20 w-[720px]">         <img src="/avatar.png">         <button><svg></svg></button> | Use responsive constraints, min/max, grid/flex, and breakpoint tokens. |
| I Orisinalitas Visual | 2.1 | 3.36 | [gradient-text] sloppy_dashboard.html:4 — Gradient/text visual cliché found. Evidence: <!doctype html> <html>   <body>     <main class="bg-gradient-to-r from-purple-500 to-violet-500 text-transparent bg-clip-text">       <h1>Da | Use domain-specific visual hierarchy instead of decorative gradients. |
| J Production Readiness | 2.5 | 2.5 | [no-error-handling] sloppy_dashboard.html:22 — Empty error handling found. Evidence: 'pending' }]         console.log(mockData)         try { throw new Error('x') } catch (e) {}       </script>     </main>   </body> </html> | Surface recoverable error states and log useful diagnostics. |

## Priority Fixes

- A Realisme Data & Domain: Move demo data behind fixtures and connect production UI to real data contracts.
- B Kejelasan Workflow: Replace dead href with a real route, disabled state explanation, or remove CTA.
- G Aksesibilitas: Add meaningful alt text or alt="" for decorative images.
- F State & Status Logic: Create a status taxonomy table with dimensions, allowed values, and UI placement.
- I Orisinalitas Visual: Use domain-specific visual hierarchy instead of decorative gradients.

## Acceptance Criteria

### A Realisme Data & Domain
- Top metrics and table values expose period/scope/source/freshness and can be traced to real data contracts.
- Re-run ADSI gate and reduce this area severity below 2 before release.

### B Kejelasan Workflow
- Each alert, metric, or problem card has a concrete CTA, owner, route, or disabled-state reason.
- Re-run ADSI gate and reduce this area severity below 2 before release.

### C Konsistensi Design System
- New UI uses shared primitives/tokens; raw style exceptions are documented and minimal.

### D Hirarki Informasi
- Heading order is sequential and visual weight matches task priority.

### E Copywriting & Lokalisasi
- User-facing copy follows one language policy and approved glossary.

### F State & Status Logic
- Status labels map to a documented taxonomy with allowed values and state transitions.

### G Aksesibilitas
- Interactive elements have accessible names, keyboard path, visible focus, and non-color-only status cues.

### H Layout & Responsiveness
- Screen is verified at mobile/tablet/desktop breakpoints without accidental horizontal overflow.

### I Orisinalitas Visual
- Visual identity supports product/domain meaning instead of generic AI-dashboard decoration.

### J Production Readiness
- Loading, empty, error, permission, observability, and automated verification are present for production paths.

## Engine Notes

- Static engine cannot see runtime interaction unless paired with `adsi collect`; use `adsi contrast` for computed contrast.
- Use static scan as CI first-pass, browser collection for DOM evidence, and agent review for workflow judgment.
