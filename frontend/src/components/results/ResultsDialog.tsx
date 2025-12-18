"use client";

import { useState } from "react";
import { Download, FileText, CheckCircle2 } from "lucide-react";
import { ExtractionResult } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Button,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Badge,
} from "@/components/ui";
import { formatTokens } from "@/lib/utils";
import { CodeViewer } from "./CodeViewer";
import { MarkdownViewer } from "./MarkdownViewer";

interface ResultsDialogProps {
  results: Record<string, ExtractionResult> | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ResultsDialog({ results, open, onOpenChange }: ResultsDialogProps) {
  const [selectedSubtype, setSelectedSubtype] = useState<string | null>(null);

  if (!results || Object.keys(results).length === 0) {
    return null;
  }

  const subtypes = Object.keys(results);
  const currentSubtype = selectedSubtype || subtypes[0];
  const currentResult = results[currentSubtype];

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadAll = () => {
    Object.entries(results).forEach(([subtype, result]) => {
      handleDownload(result.clientRules, `${subtype}_client_rules.js`);
      handleDownload(result.guidelines, `${subtype}_guidelines.md`);
    });
  };

  const totalInputTokens = Object.values(results).reduce(
    (sum, r) => sum + r.inputTokens,
    0
  );
  const totalOutputTokens = Object.values(results).reduce(
    (sum, r) => sum + r.outputTokens,
    0
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-2xl flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-green-600" />
            Extraction Complete!
          </DialogTitle>
          <DialogDescription>
            Successfully extracted rules and guidelines from {subtypes.length}{" "}
            {subtypes.length === 1 ? "category" : "categories"}
          </DialogDescription>
        </DialogHeader>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 py-4 border-y">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {subtypes.length}
            </div>
            <div className="text-sm text-muted-foreground">
              {subtypes.length === 1 ? "Category" : "Categories"}
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {formatTokens(totalInputTokens + totalOutputTokens)}
            </div>
            <div className="text-sm text-muted-foreground">Total Tokens</div>
          </div>
          <div className="text-center">
            <Button onClick={handleDownloadAll} variant="secondary" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Download All
            </Button>
          </div>
        </div>

        {/* Subtype Selector (if multiple) */}
        {subtypes.length > 1 && (
          <div className="flex gap-2 flex-wrap">
            {subtypes.map((subtype) => (
              <Badge
                key={subtype}
                variant={subtype === currentSubtype ? "default" : "secondary"}
                className="cursor-pointer px-3 py-1.5"
                onClick={() => setSelectedSubtype(subtype)}
              >
                {subtype}
              </Badge>
            ))}
          </div>
        )}

        {/* Content Tabs */}
        <div className="flex-1 min-h-0 overflow-hidden">
          <Tabs defaultValue="rules" className="h-full flex flex-col">
            <TabsList className="w-full justify-start">
              <TabsTrigger value="rules" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Client Rules
              </TabsTrigger>
              <TabsTrigger value="guidelines" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Guidelines
              </TabsTrigger>
            </TabsList>

            {/* Client Rules Tab */}
            <TabsContent value="rules" className="flex-1 min-h-0 overflow-hidden mt-4">
              <div className="h-full flex flex-col">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-sm font-medium">
                    {currentSubtype} - Client Rules
                  </div>
                  <Button
                    onClick={() =>
                      handleDownload(
                        currentResult.clientRules,
                        `${currentSubtype}_client_rules.js`
                      )
                    }
                    variant="secondary"
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
                <div className="flex-1 overflow-auto">
                  <CodeViewer code={currentResult.clientRules} language="javascript" />
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  {formatTokens(currentResult.inputTokens)} input •{" "}
                  {formatTokens(currentResult.outputTokens)} output tokens
                </div>
              </div>
            </TabsContent>

            {/* Guidelines Tab */}
            <TabsContent value="guidelines" className="flex-1 min-h-0 overflow-hidden mt-4">
              <div className="h-full flex flex-col">
                <div className="flex justify-between items-center mb-2">
                  <div className="text-sm font-medium">
                    {currentSubtype} - Guidelines
                  </div>
                  <Button
                    onClick={() =>
                      handleDownload(
                        currentResult.guidelines,
                        `${currentSubtype}_guidelines.md`
                      )
                    }
                    variant="secondary"
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
                <div className="flex-1 overflow-auto bg-muted rounded-lg p-4">
                  <MarkdownViewer content={currentResult.guidelines} />
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  {formatTokens(currentResult.inputTokens)} input •{" "}
                  {formatTokens(currentResult.outputTokens)} output tokens
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}
