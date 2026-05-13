---
name: seo-check
description: Audit SEO for HTML pages — meta tags, Open Graph, JSON-LD, headings, canonical URLs, sitemap coverage
user_invocable: true
---

# SEO Audit Skill

When invoked, perform a comprehensive SEO audit on the specified HTML file(s) or the entire site.

## Checklist

For each HTML page, check:

### Meta Tags
- `<title>` exists, is unique, 50-60 chars
- `<meta name="description">` exists, 150-160 chars
- `<meta name="viewport">` is set correctly
- `<link rel="canonical">` points to the correct URL on `1platform.pro`

### Open Graph
- `og:title`, `og:description`, `og:image`, `og:url`, `og:type` are present
- `og:image` has proper dimensions (1200x630 recommended)

### Twitter Cards
- `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image` are present

### Structured Data (JSON-LD)
- Valid JSON-LD `<script type="application/ld+json">` exists
- Schema types are appropriate (Organization, Product, WebSite, BreadcrumbList)
- Required properties are filled

### Headings
- Single `<h1>` per page
- Heading hierarchy is correct (no skipping levels)
- Headings contain relevant keywords

### Links & Navigation
- All internal links use relative paths or correct absolute URLs
- No broken anchor links
- Breadcrumbs present where appropriate

### Images
- All `<img>` tags have `alt` attributes
- Images use modern formats (WebP) where possible
- `loading="lazy"` on below-fold images

### Sitemap & Robots
- Page is included in `sitemap.xml`
- `robots.txt` allows crawling
- No `noindex` tags unless intentional

### Performance Impact on SEO
- No render-blocking resources in `<head>` without `defer`/`async`
- Critical CSS is inline or loaded efficiently
- LCP target < 2s

## Output Format

Present findings as a table:
| Issue | Severity | File | Line | Recommendation |
Use severity levels: CRITICAL, WARNING, INFO

Summarize with a score out of 100 and top 3 priorities to fix.
