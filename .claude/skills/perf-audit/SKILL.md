---
name: perf-audit
description: Audit web performance — CSS/JS optimization, resource loading, LCP, CLS, and Core Web Vitals readiness
user_invocable: true
---

# Performance Audit Skill

When invoked, analyze the site's HTML, CSS, and JS files for performance issues.

## Audit Areas

### Critical Rendering Path
- CSS loaded in `<head>` — check for render-blocking stylesheets
- JavaScript uses `defer` or `async` attributes
- No large inline `<style>` blocks (> 50KB)
- Critical CSS considerations for above-the-fold content

### CSS Performance
- Check total CSS file size (warn if > 100KB combined)
- Look for unused/duplicate selectors
- Check for expensive selectors (deep nesting > 4 levels)
- Verify CSS custom properties are used instead of repetition
- Check for `@import` chains (should use `<link>` instead)
- Animations use `transform`/`opacity` only (GPU-composited)

### JavaScript Performance
- Total JS size (warn if > 50KB for a static marketing site)
- No synchronous `<script>` tags in `<head>`
- Event listeners use passive option where appropriate
- IntersectionObserver used for scroll animations (not scroll events)
- No `document.write()` usage

### Image Optimization
- Images specify `width` and `height` (prevents CLS)
- Use `loading="lazy"` for below-fold images
- `<img>` uses `srcset` for responsive images where appropriate
- Prefer modern formats (WebP, AVIF)
- Check for oversized images (warn if > 200KB)

### Font Loading
- Fonts use `font-display: swap` or `optional`
- Fonts are preloaded with `<link rel="preload">`
- Limit number of font weights/styles loaded

### Resource Hints
- `<link rel="preconnect">` for external domains
- `<link rel="dns-prefetch">` for third-party resources

### Core Web Vitals Readiness
- **LCP**: Identify largest contentful element, check it loads fast
- **CLS**: Check for elements that could cause layout shift
- **INP**: Check for heavy JS on interactive elements

## Output Format

| Category | Issue | Impact | File | Fix |
Rate each category: GOOD / NEEDS WORK / POOR

Provide overall performance score estimate and top 5 fixes by impact.
