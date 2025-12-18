"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";

interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export function MarkdownViewer({ content, className }: MarkdownViewerProps) {
  return (
    <div
      className={cn(
        "prose prose-sm max-w-none dark:prose-invert",
        "prose-headings:font-semibold prose-headings:text-foreground",
        "prose-p:text-foreground prose-p:leading-relaxed",
        "prose-strong:text-foreground prose-strong:font-semibold",
        "prose-ul:text-foreground prose-ol:text-foreground",
        "prose-li:text-foreground prose-li:marker:text-muted-foreground",
        "prose-code:text-primary prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none",
        "prose-pre:bg-muted prose-pre:border prose-pre:border-border",
        "prose-blockquote:border-l-primary prose-blockquote:text-muted-foreground",
        "prose-hr:border-border",
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
