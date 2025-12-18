"use client";

import { FileText, Eye } from "lucide-react";
import { FileMetadata } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui";
import { formatTokens } from "@/lib/utils";

interface FilePreviewProps {
  file: FileMetadata | null;
}

export function FilePreview({ file }: FilePreviewProps) {
  if (!file) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-16 text-center animate-in fade-in duration-300">
            <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-4 animate-in zoom-in duration-500 delay-100">
              <FileText className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-base mb-2 animate-in slide-in-from-bottom-2 duration-500 delay-200">No file selected</h3>
            <p className="text-sm text-muted-foreground max-w-xs animate-in slide-in-from-bottom-2 duration-500 delay-300">
              Click on any file in the list above to view its content, language, and token count
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <Eye className="w-5 h-5" />
          Preview
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col min-h-0">
        {/* File Info */}
        <div className="mb-4 pb-4 border-b border-border">
          <div className="font-medium truncate mb-2" title={file.filename}>
            {file.filename}
          </div>
          <div className="flex items-center gap-2 flex-wrap text-sm">
            <Badge variant="secondary">
              {file.language.toUpperCase()}
            </Badge>
            <Badge variant="outline">
              {file.subtype}
            </Badge>
            <span className="text-muted-foreground">
              {formatTokens(file.tokens)} tokens
            </span>
            {file.pairId && (
              <Badge variant="outline">
                Pair #{file.pairId}
              </Badge>
            )}
          </div>
        </div>

        {/* Content Preview */}
        <div className="flex-1 min-h-0 overflow-hidden">
          <div className="text-xs font-medium text-muted-foreground mb-2">
            First 500 characters:
          </div>
          <div className="h-full overflow-y-auto bg-muted rounded-lg p-3">
            <pre className="text-xs whitespace-pre-wrap font-mono">
              {file.preview || "No preview available"}
            </pre>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
