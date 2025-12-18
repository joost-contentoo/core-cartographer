# Color Palette Reference

This document outlines the complete color system used in the portal-localiser application.

## Brand Colors

### Primary Green Scale (Contentoo Brand)
Based on Moss (#049946) and Forest (#00543E) - the main brand colors.

```css
--primary-50: #f2fdf7
--primary-100: #e1fceb
--primary-200: #d7ffc2  /* Lime */
--primary-300: #86efac
--primary-400: #11cc5b  /* Green */
--primary-500: #049946  /* Moss - Secondary Brand */
--primary-600: #037d39
--primary-700: #00543e  /* Forest - Main Brand Color (DEFAULT PRIMARY) */
--primary-800: #064e3b
--primary-900: #022c22
--primary-950: #011a14

--primary: var(--primary-700)  /* #00543e Forest */
--primary-foreground: #ffffff
```

### Secondary & Accent Colors
Fun, vibrant accent colors used throughout the interface:

```css
--color-vanilla: #ffffed
--color-petal: #fff7ff
--color-ice: #efffff
--color-yellow: #fddf47
--color-pink: #ff9fe2
--color-sky: #85e2ff
--color-orange: #ffbc00
--color-rose: #ff52c5
--color-blue: #1886e0
--color-sangria: #ff4e00  /* Used for destructive/warning actions */
--color-purple: #720052
--color-navy: #0027a3
--color-c-black: #1a1a1a
```

## Neutral Scale (Slate)
Used for backgrounds, borders, text, and UI elements:

```css
--neutral-50: #f8fafc
--neutral-100: #f1f5f9
--neutral-200: #e2e8f0
--neutral-300: #cbd5e1
--neutral-400: #94a3b8
--neutral-500: #64748b
--neutral-600: #475569
--neutral-700: #334155
--neutral-800: #1e293b
--neutral-900: #0f172a
--neutral-950: #020617
```

## Semantic Colors

### Light Mode
```css
--background: #ffffff
--foreground: #0f172a  /* Slate 900 */

--destructive: #ff4e00  /* Sangria */
--destructive-foreground: #ffffff

--muted: #f1f5f9
--muted-foreground: #64748b

--card: #ffffff
--card-foreground: #0f172a

--border: #e2e8f0
--input: #e2e8f0
--ring: var(--primary-700)  /* Focus ring color */
```

### Dark Mode
```css
--background: #020617  /* Slate 950 */
--foreground: #f8fafc  /* Slate 50 */

--primary: var(--primary-500)  /* Lighter in dark mode */
--primary-foreground: #ffffff

--muted: #1e293b
--muted-foreground: #94a3b8

--card: #0f172a
--card-foreground: #f8fafc

--border: #1e293b
--input: #1e293b
--ring: var(--primary-500)
```

## Shadows

Premium shadow system for depth and elevation:

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)
--shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05)
```

## Glassmorphism

Used for overlay effects and modern UI elements:

```css
/* Light Mode */
--glass-border: rgba(255, 255, 255, 0.2)
--glass-bg: rgba(255, 255, 255, 0.7)

/* Dark Mode */
--glass-border: rgba(255, 255, 255, 0.1)
--glass-bg: rgba(15, 23, 42, 0.6)
```

## Usage Guidelines

1. **Primary Color**: Use `var(--primary)` for main brand elements, CTAs, and interactive elements
2. **Neutral Scale**: Use for text, backgrounds, borders - provides consistent hierarchy
3. **Accent Colors**: Use sparingly for highlights, special states, or decorative elements
4. **Sangria**: Reserved for destructive actions (delete, cancel, error states)
5. **Semantic Colors**: Use `var(--card)`, `var(--border)`, etc. for consistency across themes
6. **Shadows**: Apply progressively larger shadows for higher elevation elements
