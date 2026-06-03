# ADSI Static Heuristic Rule Catalog v3

The current engine embeds rules in `adsi/engine.py` for zero-dependency portability. This catalog documents the rule families for calibration and future externalization.

| Area | Rule family | Examples |
|---|---|---|
| A | Data realism | lorem ipsum, dummy, mockData, fakeData, unscoped metric copy |
| B | Workflow | `href="#"`, empty click handler, coming soon, passive alerts |
| C | Design system | inline style, raw hex, arbitrary Tailwind classes |
| D | Hierarchy | skipped headings, repeated card/panel patterns |
| E | Copy/localization | mixed Indonesian/English, buzzwords, em dash overuse |
| F | State logic | status sprawl, loading/error/empty risk around async data |
| G | Accessibility | missing alt, icon-only button without label, clickable div, removed focus outline |
| H | Responsiveness | fixed pixel dimensions, absolute positioning, horizontal overflow |
| I | Visual originality | gradient text, purple AI palette, glassmorphism |
| J | Readiness | TODO/FIXME, debug logging, empty catch/pass blocks |

Aggregation uses severity hints, confidence, and diminishing returns. Repeated low-confidence evidence should raise suspicion but not automatically produce a severe score.
