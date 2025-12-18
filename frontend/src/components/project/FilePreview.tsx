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
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <FileText className="w-16 h-16 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">
              Select a file to preview its content
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
