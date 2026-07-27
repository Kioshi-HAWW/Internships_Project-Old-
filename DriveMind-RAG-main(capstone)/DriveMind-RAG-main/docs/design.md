# DESIGN — Visual Style (for optional chat UI)

MVP is API-first, but if/when a simple chat frontend is built, use this
as the style baseline.

## 1. Theme
- Dark-first, calm "reading room" feel — this is a personal library tool,
  not a flashy consumer app.
- Minimal chrome, content (the answer + sources) is the hero.

## 2. Colors

| Role            | Color        | Hex        |
|------------------|--------------|------------|
| Background       | Near-black   | `#0F1115`  |
| Surface / card    | Dark slate   | `#181B21`  |
| Primary text      | Off-white    | `#EAEAEA`  |
| Secondary text    | Muted gray   | `#9AA0A8`  |
| Accent (brand)    | Warm amber   | `#D9A441`  |
| Accent hover      | Deeper amber | `#B8842F`  |
| Success           | Soft green   | `#5FAD7A`  |
| Error             | Muted red    | `#D96C6C`  |
| Border/divider    | Subtle gray  | `#2A2E36`  |

(Amber accent = "library lamp light" feel; swap for any accent color you
prefer — the neutral base stays the same.)

## 3. Typography
- **Headings:** `Fraunces` or `Source Serif 4` (serif — evokes books/library)
- **Body / UI:** `Inter` or `IBM Plex Sans` (clean, highly legible)
- **Code / citations:** `IBM Plex Mono`

Sizes (base 16px):
- H1: 28px / 700
- H2: 20px / 600
- Body: 16px / 400, line-height 1.6
- Small/meta (source labels): 13px / 500, secondary text color

## 4. Layout Principles
- Single-column chat, max-width ~760px, centered
- Answer bubble: surface color, generous padding (20px), rounded 12px
- **Sources shown as small pill/chip list below each answer** — clicking
  opens the Drive link
- Input bar fixed at bottom, minimal border, amber focus ring
- No unnecessary animation — subtle fade-in on new messages only

## 5. Tone
- Answers should visually read like reference material: clear paragraph
  breaks, citations always visible, no dense walls of text.
