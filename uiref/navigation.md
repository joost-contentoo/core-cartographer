# Navigation Pattern Reference

This document describes the unique navigation system used in the portal-localiser application.

## Anchor Rail Navigation

The application uses a fixed left sidebar ("Anchor Rail") for navigation with a visual progress indicator.

### Structure

```
┌─────────────────────┐
│  Logo               │
│                     │
│  ┌─────────┐       │
│  │  SEO    │ ●─┐   │
│  └─────────┘   │   │
│                 ├── Progress Line
│  ┌─────────┐   │   │
│  │  Input  │ ●─┤   │
│  └─────────┘   │   │
│                 │   │
│  ┌─────────┐   │   │
│  │ Compare │ ●─┘   │
│  └─────────┘       │
│                     │
│  ┌─────────┐       │
│  │ Ref.    │       │
│  └─────────┘       │
│                     │
│      [Logs]         │
└─────────────────────┘
```

### Implementation

```tsx
<div className="w-20 flex flex-col items-center py-16 bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl border-r border-gray-200 dark:border-gray-800 z-50 h-screen sticky top-0">

  {/* Logo */}
  <div className="mb-10">
    {/* Logo component */}
  </div>

  {/* Main Flow - with progress line */}
  <div className="flex flex-col items-center relative">
    {/* Progress track */}
    <div className="absolute left-1/2 -translate-x-1/2 top-5 bottom-5 w-0.5 bg-gray-100 dark:bg-gray-800 rounded-full" />

    {/* Progress fill */}
    <div
      className="absolute left-1/2 -translate-x-1/2 top-5 w-0.5 bg-primary rounded-full transition-all duration-150"
      style={{ height: `calc(${scrollProgress * 100}% - 2.5rem)` }}
    />

    {/* Navigation items */}
  </div>
</div>
```

---

## Navigation Button Pattern

Each navigation item includes:
1. Icon with active/hover states
2. Sliding label tooltip on hover
3. Active state glow effect
4. Smooth scroll to section

```tsx
<button
  onClick={() => handleNavigate(item.id)}
  className="group relative flex items-center justify-center"
>
  {/* Active glow */}
  {isActive && (
    <div className="absolute inset-0 bg-primary/20 rounded-xl blur-md animate-pulse" />
  )}

  {/* Icon container */}
  <div className={`
    relative w-10 h-10 flex items-center justify-center rounded-xl
    transition-all duration-300 border
    ${isActive
      ? 'bg-white border-primary text-primary shadow-lg scale-110'
      : 'bg-white border-gray-200 text-gray-400 hover:text-gray-600'}
  `}>
    <item.icon className="w-5 h-5" />
  </div>

  {/* Sliding tooltip */}
  <div className="absolute left-full ml-4 pointer-events-none">
    <div className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-gray-900 text-white opacity-0 group-hover:opacity-100 transition-all duration-300">
      {item.label}
    </div>
  </div>
</button>
```

---

## Active Section Detection

Uses Intersection Observer:

```tsx
useEffect(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveSection(entry.target.id);
        }
      });
    },
    { root: container, threshold: 0.5 }
  );

  const sections = document.querySelectorAll('#seo-workspace, #input-workspace, ...');
  sections.forEach((section) => observer.observe(section));

  return () => observer.disconnect();
}, []);
```

---

## Scroll Progress Indicator

```tsx
const handleScroll = () => {
  const { scrollTop, scrollHeight, clientHeight } = container;
  const progress = scrollTop / (scrollHeight - clientHeight);
  setScrollProgress(Math.min(Math.max(progress, 0), 1));
};
```

---

## Navigation Items

```tsx
const flowItems = [
  { id: 'seo-workspace', icon: Search, label: 'SEO' },
  { id: 'input-workspace', icon: PenTool, label: 'Input' },
  { id: 'comparison-deck', icon: Columns, label: 'Compare' },
];

const referenceItem = {
  id: 'reference-drawer',
  icon: Book,
  label: 'Reference'
};

const testingItems = [
  { id: 'log-view', icon: ScrollText, label: 'Logs', isRed: true },
];
```

---

## Main Container Layout

```tsx
<main className="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
  <AnchorRail />

  <div className="flex-1 flex flex-col overflow-y-auto scroll-smooth">
    <div className="constrained-container py-16 space-y-24">
      <div id="seo-workspace" className="scroll-mt-16 h-[calc(100vh-8rem)]">
        <SeoWorkspace />
      </div>
      {/* More sections */}
    </div>
  </div>
</main>
```

---

## Design Principles

1. **Vertical Navigation**: Optimized for vertical scrolling
2. **Visual Progress**: Line shows position in workflow
3. **Active State**: Clear indication of current section
4. **Hover Tooltips**: Labels appear on hover to save space
5. **Smooth Scrolling**: Natural transitions between sections
6. **Separated Groups**: Flow items connected, reference/logs separate
7. **Full-height Sections**: Each section takes full viewport
8. **Sticky Sidebar**: Navigation stays fixed while content scrolls
9. **Glassmorphism**: Semi-transparent background with blur
10. **Accessible**: ARIA labels and keyboard navigation

---

## Icons (Lucide React)

```tsx
import {
  PenTool,    // Input
  Columns,    // Compare
  Book,       // Reference
  ScrollText, // Logs
  Search,     // SEO
} from 'lucide-react';
```

All icons: `w-5 h-5` (20px)
