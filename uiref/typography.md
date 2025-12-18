# Typography Reference

This document outlines the typography system used in the portal-localiser application.

## Font Family

### Primary Font: Inter
The application uses the **Inter** font family from Google Fonts.

```typescript
import { Inter } from "next/font/google";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});
```

```css
--font-sans: var(--font-inter);

body {
  font-family: var(--font-sans), Arial, Helvetica, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### Monospace Font
For code, markdown input, and technical content, use monospace:

```css
font-family: monospace;
```

## Type Scale

### Headings
```tsx
// Section Headers (Card/Workspace Titles)
"text-lg font-semibold tracking-tight"
// Example: "Content Input", "SEO Research"

// Descriptions
"text-xs text-neutral-500 dark:text-neutral-400 font-medium"
// Example: "Provide your source content and instructions"
```

### Labels
```css
/* Form Labels (Uppercase Small Caps) */
text-xs font-semibold uppercase tracking-wider text-gray-500
```

### Body Text
```tsx
"text-sm"   // Small (14px)
"text-base" // Base (16px)
"text-lg"   // Large (18px)
```

### Button Sizes
```tsx
size: 'sm' -> "text-sm"
size: 'md' -> "text-base"
size: 'lg' -> "text-lg"
```

## Font Weights

```css
font-medium: 500   /* Labels, subtle emphasis */
font-semibold: 600 /* Section headers, form labels */
font-bold: 700     /* Logo, strong emphasis */
```

## Letter Spacing

```css
tracking-tight: -0.025em   /* Headings - makes them feel more compact */
tracking-wider: 0.05em     /* Uppercase labels - improves readability */
letter-spacing: -0.5px     /* Logo text - tighter for branding */
```

## Text Colors

### Light Mode
```css
--foreground: #0f172a  /* Slate 900 - primary text */
text-neutral-900       /* Headings */
text-neutral-500       /* Descriptions, muted text */
```

### Dark Mode
```css
--foreground: #f8fafc  /* Slate 50 - primary text */
dark:text-neutral-100  /* Headings */
dark:text-neutral-400  /* Descriptions, muted text */
```

## Logo Typography

```tsx
// Number "1"
<span className="text-[10px] font-medium opacity-90">1</span>

// "Lo" text
<span className="font-bold text-xl tracking-tight">Lo</span>
```
