"use client";

import { FileText, Eye } from "lucide-react";
import { FileMetadata } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui";
import { formatTokens } from "@/lib/utils";

interface FilePreviewProps {
  file: FileMetadata | null;
  className?: string;
}

export function FilePreview({ file, className }: FilePreviewProps) {
  // If no file selected, show empty state
  if (!file) {
    return (
      <div className={`flex flex-col items-center justify-center h-full p-8 text-center animate-in fade-in duration-300 bg-muted/20 ${className}`}>
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4 text-muted-foreground/50">
          <FileText className="w-8 h-8" />
        </div>
        <h3 className="font-semibold text-lg text-muted-foreground">Select a document</h3>
        <p className="text-sm text-muted-foreground/70 max-w-xs mt-2">
          Choose a file from the list to preview its content.
        </p>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-card ${className}`}>
      {/* File Info Header */}
      <div className="px-6 py-4 border-b border-border flex flex-col justify-between shrink-0">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold truncate leading-tight" title={file.filename}>
              {file.filename}
            </h3>
            <div className="flex items-center gap-2 mt-2 flex-wrap text-sm">
              <Badge variant="secondary" className="font-normal bg-primary-100 text-primary-800 hover:bg-primary-200">
                {file.language.toUpperCase()}
              </Badge>
              <span className="text-muted-foreground px-2 py-0.5 bg-muted rounded text-xs font-mono">
                {formatTokens(file.tokens)} tokens
              </span>
              {file.pairId && (
                <Badge variant="outline" className="text-xs">
                  Pair #{file.pairId}
                </Badge>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end">
            <Badge variant="outline" className="uppercase text-[10px] tracking-wider font-semibold">
              {file.subtype}
            </Badge>
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-auto bg-muted/10 p-4 md:p-6 min-h-0">
        <div className="bg-white dark:bg-zinc-900 rounded-lg border shadow-sm p-6 min-h-full">
          <div className="text-xs font-medium text-muted-foreground mb-4 uppercase tracking-wider">
            Content Preview
          </div>
          <pre className="text-sm whitespace-pre-wrap font-mono text-foreground leading-relaxed">
            {file.preview || "No preview available for this file."}
          </pre>
        </div>
      </div>
    </div>
  );
}
