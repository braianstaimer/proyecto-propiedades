---
name: a11y-check
description: Audit accessibility (WCAG 2.1 AA) — ARIA, color contrast, keyboard navigation, screen reader support
user_invocable: true
---

# Accessibility Audit Skill

When invoked, audit HTML pages for WCAG 2.1 Level AA compliance.

## Audit Areas

### Perceivable
- All images have meaningful `alt` text (not "image" or empty for decorative)
- Videos/audio have captions or transcripts
- Color is not the only means of conveying information
- Text contrast ratio meets 4.5:1 (normal text) / 3:1 (large text)
- Check CSS custom properties for contrast: background vs text colors
- Content is readable at 200% zoom

### Operable
- All interactive elements reachable via keyboard (Tab/Shift+Tab)
- Focus indicators visible (`:focus-visible` styles exist)
- No keyboard traps
- Skip navigation link present
- Mobile menu is keyboard accessible
- Dropdown menus handle Escape key
- No time-limited interactions without extension option

### Understandable
- `<html lang="en">` is set
- Form inputs have visible labels
- Error messages are clear and associated with fields
- Navigation is consistent across pages
- Abbreviations and jargon are explained

### Robust
- Valid HTML (proper nesting, no duplicate IDs)
- ARIA roles used correctly (not redundant with semantic HTML)
- `aria-label` / `aria-labelledby` on interactive elements without visible labels
- `aria-expanded` on toggle buttons (mobile menu, accordions)
- `aria-current="page"` on active nav links
- `role="navigation"`, `role="main"` only where semantic elements aren't used
- Live regions (`aria-live`) for dynamic content updates

### Dark Theme Specific
- Ensure sufficient contrast in dark mode (#0a0a0a background)
- Glow effects don't reduce text readability
- Focus indicators visible against dark backgrounds
- Gradient text remains readable

## Output Format

| Rule | Level | Issue | Element | File:Line | Fix |

Levels: A, AA, AAA
Severity: FAIL (must fix), WARN (should fix), PASS

Summary: X issues found (Y critical, Z warnings). Compliance estimate: X/100.
