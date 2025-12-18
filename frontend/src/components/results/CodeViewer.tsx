"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface CodeViewerProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
}

export function CodeViewer({
  code,
  language = "javascript",
  showLineNumbers = true,
}: CodeViewerProps) {
  return (
    <div className="rounded-lg overflow-hidden border border-border">
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        showLineNumbers={showLineNumbers}
        customStyle={{
          margin: 0,
          padding: "1rem",
          fontSize: "0.75rem",
          lineHeight: "1.5",
          background: "rgb(30, 30, 30)",
        }}
        lineNumberStyle={{
          minWidth: "3em",
          paddingRight: "1em",
          color: "rgb(133, 133, 133)",
          userSelect: "none",
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
