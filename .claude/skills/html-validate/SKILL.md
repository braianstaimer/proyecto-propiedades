---
name: html-validate
description: Validate HTML pages for W3C compliance, semantic correctness, and best practices
user_invocable: true
---

# HTML Validation Skill

When invoked, validate the specified HTML file(s) for correctness and best practices.

## Validation Checks

### Structural Validity
- Valid HTML5 doctype (`<!DOCTYPE html>`)
- `<html lang="en">` attribute present
- Proper `<head>` and `<body>` structure
- All tags properly closed/self-closing
- No duplicate IDs on the page
- Valid nesting (no `<div>` inside `<p>`, etc.)

### Semantic HTML
- Use of semantic elements: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- `<main>` element exists and is unique
- Forms have proper `<label>` elements
- Tables use `<thead>`, `<tbody>`, `<th scope>`
- Lists use `<ul>`/`<ol>`/`<li>` appropriately

### Links & Resources
- No broken internal links (check file exists)
- CSS files referenced correctly
- JS files referenced with `defer` or at end of body
- No mixed content (http:// in https:// page)

### Character Encoding
- `<meta charset="UTF-8">` present
- No invalid Unicode characters

### Forms
- All inputs have associated labels
- Required fields marked with `required` attribute
- Form actions point to valid endpoints

## Output Format

List issues grouped by file:
```
filename.html
  Line XX: [ERROR|WARN|INFO] Description
```

Provide a summary count of errors, warnings, and info items.
