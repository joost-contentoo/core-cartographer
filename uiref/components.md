# Component Patterns Reference

This document outlines the UI component patterns and design system used in the portal-localiser application.

## Core Components

### Button

Premium button with multiple variants and loading states.

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}
```

**Base Styles:**
```css
rounded-xl
font-medium
transition-all duration-200
focus:outline-none focus:ring-2 focus:ring-offset-2
disabled:opacity-50 disabled:cursor-not-allowed
active:scale-[0.98]  /* Subtle press effect */
```

**Variants:**

```tsx
// Primary - Main actions
'primary':
  bg-primary text-primary-foreground
  shadow-lg shadow-primary/25
  hover:bg-primary-500 hover:shadow-xl hover:shadow-primary/30

// Secondary - Alternative actions
'secondary':
  bg-white text-neutral-900 border border-neutral-200
  shadow-sm hover:bg-neutral-50
  dark:bg-neutral-800 dark:text-neutral-100

// Ghost - Subtle actions
'ghost':
  bg-transparent text-neutral-600
  hover:bg-neutral-100 hover:text-neutral-900

// Destructive - Delete/cancel
'destructive':
  bg-destructive text-destructive-foreground
  shadow-sm hover:bg-red-600

// Outline - Bordered variant
'outline':
  bg-transparent border border-neutral-200
  text-neutral-700 hover:bg-neutral-50
```

**Sizes:**
```tsx
'sm': 'h-9 px-3 text-sm'
'md': 'h-11 px-5 text-base'
'lg': 'h-14 px-8 text-lg'
'icon': 'h-10 w-10 p-2'
```

**Usage Example:**
```tsx
<Button
  variant="primary"
  size="lg"
  isLoading={isLoading}
  leftIcon={<Search className="w-5 h-5" />}
  onClick={handleAction}
>
  Research SEO
</Button>
```

---

### Card

Flexible container with glassmorphism support.

```tsx
interface CardProps {
  variant?: 'default' | 'glass' | 'flat';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}
```

**Base Styles:**
```css
rounded-[24px]  /* Large, modern border radius */
overflow-hidden
transition-all duration-300
```

**Variants:**

```tsx
// Default - Standard card
'default':
  bg-white dark:bg-neutral-900
  border border-neutral-300 dark:border-neutral-700
  shadow-lg shadow-neutral-900/10

// Glass - Premium glassmorphism effect
'glass':
  bg-white/95 dark:bg-neutral-900/60
  backdrop-blur-xl
  border-2 border-neutral-300/60
  shadow-xl shadow-neutral-900/10

// Flat - Minimal card
'flat':
  bg-neutral-50 dark:bg-neutral-800/50
  border border-neutral-100 dark:border-neutral-800
```

**Padding:**
```tsx
'none': ''        // No padding
'sm': 'p-4'       // 16px
'md': 'p-6'       // 24px
'lg': 'p-8'       // 32px
```

---

### Badge

Status indicators and labels.

```tsx
interface BadgeProps {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'outline';
  size?: 'sm' | 'md';
}
```

**Variants:**
```tsx
'default': 'bg-neutral-100 text-neutral-800'
'primary': 'bg-primary-50 text-primary-700 border border-primary-200'
'success': 'bg-green-50 text-green-700 border border-green-200'
'warning': 'bg-amber-50 text-amber-700 border border-amber-200'
'error': 'bg-red-50 text-red-700 border border-red-200'
'outline': 'bg-transparent border border-neutral-200'
```

**Sizes:**
```tsx
'sm': 'px-2 py-0.5 text-xs'
'md': 'px-2.5 py-0.5 text-sm'
```

---

## Layout Patterns

### Constrained Container

Premium responsive container:

```css
.constrained-container {
  width: min(100%, 1440px);
  margin-left: auto;
  margin-right: auto;
  padding-left: clamp(1.5rem, 3vw, 3.5rem);
  padding-right: clamp(1.5rem, 3vw, 3.5rem);
}
```

### Card Header Pattern

```tsx
<div className="px-8 py-6 border-b border-neutral-200/60 dark:border-neutral-800/60 shrink-0 flex justify-between items-center bg-white/50 dark:bg-neutral-900/50 backdrop-blur-sm">
  <div className="flex items-center gap-3">
    <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg text-primary-600 dark:text-primary-400">
      <Icon className="w-5 h-5" />
    </div>
    <div>
      <h2 className="text-lg font-semibold tracking-tight">Title</h2>
      <p className="text-xs text-neutral-500 dark:text-neutral-400 font-medium">
        Description
      </p>
    </div>
  </div>
  <Button variant="ghost" size="sm">Action</Button>
</div>
```

### Form Input Pattern

```tsx
<div>
  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
    Field Label
  </label>
  <input
    className="w-full bg-white dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-xl px-4 py-3 font-mono text-sm shadow-sm hover:border-primary/50 focus:shadow-[0_0_20px_rgba(0,166,157,0.1)] focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all duration-200"
  />
</div>
```

---

## Special Effects

### Glassmorphism

```css
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
}
```

### Custom Scrollbar

```css
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 4px;
}

/* Firefox */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.3) transparent;
}
```

---

## Animation Patterns

### Keyframes

```css
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes scale-in {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
```

### Interactive Animations

```tsx
active:scale-[0.98]           // Button press
group-hover:scale-110         // Icon hover
transition-all duration-200   // Smooth transitions
```

---

## Design Principles

1. **Large Border Radius**: Use `rounded-xl` (12px) or `rounded-[24px]` (24px)
2. **Generous Spacing**: Use 6-8 spacing units (24-32px)
3. **Subtle Shadows**: Layer shadows for depth (`shadow-lg shadow-primary/25`)
4. **Smooth Transitions**: 200-300ms transitions on interactive elements
5. **Focus States**: Always include visible focus rings
6. **Dark Mode**: Every component supports dark mode
7. **Loading States**: Show loading indicators for async actions
8. **Icon Integration**: Use Lucide React icons at 16px or 20px
9. **Backdrop Blur**: Use for overlays and glass effects
10. **Color Opacity**: Use `/` notation (e.g., `bg-primary/25`)
