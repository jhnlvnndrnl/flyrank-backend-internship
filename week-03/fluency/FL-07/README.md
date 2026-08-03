# Identity Kit — Elvin

**Track:** AI Fluency — Week 03
**Deliverable:** Visual identity kit (type, palette, logo/favicon, style note)
**Source of truth:** pulled directly from `global.css` on the live site (`learn.jeendrenal.online`), so the kit and the build can't drift apart.

---

## 1. Type

| Role             | Font    | Weight(s)         |
|-------------------|---------|--------------------|
| Heading / Display | Manrope | Bold / ExtraBold   |
| Body              | Inter   | Regular / Medium   |

Two fonts, already imported in the codebase.

## 2. Palette

| Name   | Hex       | Role                                       |
|--------|-----------|---------------------------------------------|
| Navy   | `#0f172a` | Near-black text                              |
| White  | `#ffffff` | Near-white background                        |
| Indigo | `#4338ca` | Main color (CTAs, headers, structure)        |
| Violet | `#7c3aed` | Accent — pairs with Indigo in gradients only |

4 colors, taken straight from the `:root` variables (`--navy`, `--indigo`, `--violet`), keeping the kit and the actual code in sync.

## 3. Logo / Favicon

**`E`** monogram in Manrope ExtraBold, set on an Indigo-to-Violet diagonal gradient — the same gradient already used for `.gradient-text` and `.gradient-bg` on the site. Scales cleanly from a 64px header mark down to a 16px favicon.

## 4. Style Note

> Manrope headlines over Inter body copy, navy on white, with an indigo-to-violet gradient carrying the main color and marking key accents.
> The mood is a modern engineering studio: confident, gradient-lit, built for products that feel current rather than austere.

---

*Full interactive one-pager (`identity-kit.html`) available as the working reference — swap in these tokens anywhere new pages or case studies are built to keep everything consistent.*