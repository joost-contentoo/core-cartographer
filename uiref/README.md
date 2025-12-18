# Portal Localiser UI Reference

This folder contains extracted UI/styling reference documentation from the `portal-localiser` project. Use these references to create Node.js frontend apps with the same visual style.

## Contents

### [colors.md](./colors.md)
Complete color palette including:
- **Primary Green Scale**: Forest (#00543e) and Moss (#049946) brand colors
- **Accent Colors**: Vanilla, Petal, Ice, Yellow, Pink, Sky, Orange, Sangria, etc.
- **Neutral Scale**: Slate color scale for UI elements
- **Semantic Colors**: Light/dark mode variants
- **Shadows**: Premium shadow system
- **Glassmorphism**: Overlay and glass effect colors

### [typography.md](./typography.md)
Typography system including:
- **Font**: Inter from Google Fonts
- **Type Scale**: Headings, body text, labels
- **Font Weights**: Medium (500), Semibold (600), Bold (700)
- **Letter Spacing**: Tracking for different contexts
- **Text Colors**: Light and dark mode variants

### [logo.md](./logo.md)
Logo specifications:
- **Design**: Forest green square with "1" and "Lo" text
- **SVG Code**: Favicon implementation
- **React Component**: Logo component code
- **Sizing Variations**: Small, medium, large versions
- **Colors & Typography**: Exact specifications

### [components.md](./components.md)
Component library patterns:
- **Button**: Primary, secondary, ghost, destructive, outline variants
- **Card**: Default, glass, flat variants with glassmorphism
- **Badge**: Status indicators and labels
- **Layout Patterns**: Constrained containers, card headers, form inputs
- **Special Effects**: Glassmorphism, custom scrollbars
- **Animations**: Keyframes and interactive states

### [navigation.md](./navigation.md)
Navigation system:
- **Anchor Rail**: Fixed left sidebar with logo and navigation
- **Progress Indicator**: Visual scroll progress line
- **Navigation Buttons**: Icon buttons with tooltips
- **Active Detection**: Intersection Observer implementation
- **Smooth Scrolling**: Section-to-section navigation
- **Icons**: Lucide React icon library

## Key Design Characteristics

### Color Scheme
- **Primary**: Forest green (#00543e)
- **Style**: Clean, modern, professional
- **Dark Mode**: Full support with automatic switching

### Typography
- **Font**: Inter (Google Fonts)
- **Style**: Clean, readable, with good hierarchy
- **Weights**: Medium, Semibold, Bold

### UI Style
- **Border Radius**: Large (12-24px) for modern look
- **Shadows**: Subtle, layered for depth
- **Spacing**: Generous (24-32px) for comfort
- **Glassmorphism**: Premium backdrop blur effects
- **Animations**: Smooth 200-300ms transitions

### Component Style
- **Buttons**: Rounded-xl with hover effects and loading states
- **Cards**: Large border radius (24px) with glass variants
- **Inputs**: Rounded-xl with focus glow effects
- **Navigation**: Fixed sidebar with scroll progress

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS v4 with CSS variables
- **Icons**: Lucide React
- **Fonts**: Google Fonts (Inter)
- **Components**: Custom component library

## CSS Architecture

Uses CSS custom properties (variables) for theming:

```css
:root {
  --primary-700: #00543e;
  --primary: var(--primary-700);
  --background: #ffffff;
  --foreground: #0f172a;
  /* etc. */
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #020617;
    --foreground: #f8fafc;
    /* etc. */
  }
}
```

Tailwind CSS classes reference these variables:
```tsx
className="bg-primary text-primary-foreground"
```

## Implementation Notes

1. **Tailwind Config**: Uses inline `@theme` directive for CSS variable integration
2. **Font Loading**: Next.js font optimization with `next/font/google`
3. **Dark Mode**: Uses `prefers-color-scheme` media query (system preference)
4. **Glassmorphism**: Requires `backdrop-filter` CSS property support
5. **Icons**: Lucide React provides consistent icon style at 16px or 20px

## Usage

To replicate this style in a new Node.js frontend app:

1. Install dependencies:
   ```bash
   npm install tailwindcss @tailwindcss/typography lucide-react
   ```

2. Copy color variables from `colors.md` to your global CSS

3. Set up Inter font from `typography.md`

4. Use component patterns from `components.md` as templates

5. Implement navigation from `navigation.md` if needed

6. Use the logo design from `logo.md` for branding

## Source

Extracted from: `/Users/joost/github/portal-localiser`
Date: December 2025
