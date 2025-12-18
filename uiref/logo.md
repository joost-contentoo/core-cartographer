# Logo Reference

This document describes the logo design used in the portal-localiser application.

## Logo Design

The logo consists of:
1. A forest green square background with rounded corners
2. A small "1" number in the top-left
3. Large "Lo" text centered below

### SVG Favicon

```svg
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <rect width="48" height="48" rx="4" fill="#00543e"/>
  <text x="6" y="13" font-family="Arial, sans-serif" font-size="10" font-weight="500" fill="rgba(255,255,255,0.9)">1</text>
  <text x="24" y="33" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="white" text-anchor="middle" letter-spacing="-0.5">Lo</text>
</svg>
```

### React Component

```tsx
<div className="w-12 h-12 bg-primary rounded-md flex flex-col items-center justify-center text-white shadow-lg shadow-primary/20 transition-transform duration-300 group-hover:scale-105 relative">
  <span className="absolute top-0.5 left-1 text-[10px] font-medium opacity-90">1</span>
  <span className="font-bold text-xl mt-1 tracking-tight">Lo</span>
</div>
```

## Logo Specifications

### Dimensions
- Width: 48px
- Height: 48px
- Border radius: 4px (favicon) / 6px (`rounded-md` in React)

### Colors
- Background: `#00543e` (Forest green - primary-700)
- "1" text: `rgba(255,255,255,0.9)` (90% white)
- "Lo" text: `#ffffff` (100% white)

### Typography
- Font family: Arial, sans-serif
- "1" number: 10px, weight 500, top-left position
- "Lo" text: 20px, weight 700, centered, letter-spacing -0.5px

### Shadow
```css
shadow-lg shadow-primary/20
/* Equivalent to: */
box-shadow: 0 10px 15px -3px rgba(0, 84, 62, 0.2),
            0 4px 6px -4px rgba(0, 84, 62, 0.2);
```

## Logo Meaning

- **"1"**: Represents being #1 or first-class service
- **"Lo"**: Short for "Localisation" or "Localiser"
- **Forest Green**: Represents the Contentoo brand color

## Sizing Variations

```tsx
// Small (32px)
<div className="w-8 h-8 bg-primary rounded">
  <span className="text-[8px]">1</span>
  <span className="text-sm font-bold">Lo</span>
</div>

// Medium (48px) - Default
<div className="w-12 h-12 bg-primary rounded-md">
  <span className="text-[10px]">1</span>
  <span className="text-xl font-bold">Lo</span>
</div>

// Large (64px)
<div className="w-16 h-16 bg-primary rounded-lg">
  <span className="text-xs">1</span>
  <span className="text-2xl font-bold">Lo</span>
</div>
```
