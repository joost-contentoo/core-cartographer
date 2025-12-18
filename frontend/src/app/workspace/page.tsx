"use client";

import { useState, useCallback } from "react";
import { useProjectStore } from "@/lib/store";
import { api } from "@/lib/api";
import { formatTokens, formatCost, isSupportedFileType } from "@/lib/utils";
import type { SSEEvent } from "@/lib/api";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Badge,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui";
import { Upload, FileText, Loader2, Sparkles, Search, Trash2, Plus } from "lucide-react";

export default function WorkspacePage() {
  const {
    clientName,
    setClientName,
    files,
    addFile,
    updateFile,
    removeFile,
    subtypes,
    addSubtype,
    settings,
    extraction,
    setExtractionProgress,
    setResults,
    results,
    totalTokens,
    estimatedCost,
  } = useProjectStore();

  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newSubtype, setNewSubtype] = useState("");

  // File upload handler
  const handleFileUpload = useCallback(
    async (fileList: FileList | null) => {
      if (!fileList || fileList.length === 0) return;

      setUploading(true);
      setError(null);

      for (const file of Array.from(fileList)) {
        if (!isSupportedFileType(file.name)) {
          setError(`Unsupported file type: ${file.name}`);
          continue;
        }

        try {
          const result = await api.parseFile(file);

          if (result.success) {
            addFile({
              fileId: result.fileId,
              filename: result.filename,
              language: "en",
              subtype: "general",
              pairId: null,
              tokens: result.tokens,
              preview: result.preview,
              status: "ready",
            });
          } else {
            setError(result.error || "Failed to parse file");
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : "Upload failed");
        }
      }

      setUploading(false);
    },
    [addFile]
  );

  // Auto-detect handler
  const handleAutoDetect = useCallback(async () => {
    if (files.length === 0) return;

    try {
      setError(null);
      const result = await api.runAutoDetect(files.map((f) => f.fileId));

      result.files.forEach((detectedFile) => {
        updateFile(detectedFile.file_id, {
          language: detectedFile.language,
          pairId: detectedFile.pair_id,
        });
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Auto-detect failed");
    }
  }, [files, updateFile]);

  // Extraction handler
  const handleExtraction = useCallback(async () => {
    if (!clientName || files.length === 0) {
      setError("Please provide a client name and upload files");
      return;
    }

    setExtracting(true);
    setError(null);
    setExtractionProgress({
      status: "running",
      currentSubtype: null,
      completedSubtypes: [],
      totalSubtypes: subtypes.length,
    });

    const documentSets = subtypes.map((subtype) => ({
      subtype,
      files: files
        .filter((f) => f.subtype === subtype)
        .map((f) => ({
          fileId: f.fileId,
          language: f.language,
          pairId: f.pairId,
        })),
    }));

    api.extractWithSSE(
      {
        clientName,
        documentSets: documentSets.filter((ds) => ds.files.length > 0),
        batchProcessing: settings.batchProcessing,
        debugMode: settings.debugMode,
      },
      (event: SSEEvent) => {
        switch (event.type) {
          case "started":
            setExtractionProgress({
              status: "running",
              totalSubtypes: event.subtypes?.length || 0,
            });
            break;

          case "progress":
            setExtractionProgress({
              currentSubtype: event.subtype || null,
            });
            break;

          case "subtype_complete":
            setExtractionProgress({
              completedSubtypes: [...extraction.completedSubtypes, event.subtype || ""],
            });
            break;

          case "complete":
            if (event.results) {
              const convertedResults: Record<string, any> = {};
              Object.entries(event.results).forEach(([subtype, result]) => {
                convertedResults[subtype] = {
                  clientRules: result.client_rules,
                  guidelines: result.guidelines,
                  inputTokens: result.input_tokens,
                  outputTokens: result.output_tokens,
                };
              });
              setResults(convertedResults);
            }
            setExtractionProgress({
              status: "complete",
              currentSubtype: null,
            });
            setExtracting(false);
            break;

          case "error":
            setError(event.message || "Extraction failed");
            setExtractionProgress({
              status: "error",
              error: event.message,
            });
            setExtracting(false);
            break;
        }
      },
      (err: Error) => {
        setError(err.message);
        setExtractionProgress({
          status: "error",
          error: err.message,
        });
        setExtracting(false);
      }
    );
  }, [
    clientName,
    files,
    subtypes,
    settings,
    extraction.completedSubtypes,
    setExtractionProgress,
    setResults,
  ]);

  const handleAddSubtype = () => {
    if (newSubtype && !subtypes.includes(newSubtype)) {
      addSubtype(newSubtype);
      setNewSubtype("");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-primary-800 mb-2">
            Core Cartographer
          </h1>
          <p className="text-primary-600">
            Extract localization rules and guidelines from documentation
          </p>
        </header>

        {/* Error Banner */}
        {error && (
          <Card className="mb-6 border-destructive bg-destructive/10">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <span className="text-destructive text-lg">⚠️</span>
                <div className="flex-1">
                  <p className="text-destructive font-medium">{error}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                >
                  ✕
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Panel (2 columns) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Client Name */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Project Details</CardTitle>
                <CardDescription>Enter the client name to begin</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="client-name">Client Name</Label>
                  <Input
                    id="client-name"
                    value={clientName}
                    onChange={(e) => setClientName(e.target.value)}
                    placeholder="e.g., Acme Corporation"
                  />
                </div>
              </CardContent>
            </Card>

            {/* File Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Upload Files</CardTitle>
                <CardDescription>
                  Add your documentation files (PDF, DOCX, TXT, MD)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border-2 border-dashed border-primary-300 rounded-xl p-8 text-center hover:border-primary-500 transition-colors">
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                    disabled={uploading}
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer flex flex-col items-center gap-3"
                  >
                    {uploading ? (
                      <Loader2 className="w-12 h-12 text-primary animate-spin" />
                    ) : (
                      <Upload className="w-12 h-12 text-primary" />
                    )}
                    <div>
                      <p className="text-primary-700 font-medium">
                        {uploading
                          ? "Uploading..."
                          : "Click to upload or drag files here"}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">
                        PDF, DOCX, TXT, MD (max 10MB per file)
                      </p>
                    </div>
                  </label>
                </div>
              </CardContent>
            </Card>

            {/* File List */}
            {files.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Files ({files.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {files.map((file) => (
                      <div
                        key={file.fileId}
                        className="flex items-center gap-3 p-3 bg-muted rounded-lg hover:bg-muted/80 transition-colors"
                      >
                        <FileText className="w-5 h-5 text-primary shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{file.filename}</div>
                          <div className="text-sm text-muted-foreground flex items-center gap-2 flex-wrap">
                            <Badge variant="secondary">
                              {file.language.toUpperCase()}
                            </Badge>
                            <span>{formatTokens(file.tokens)} tokens</span>
                            {file.pairId && (
                              <Badge variant="outline">Pair #{file.pairId}</Badge>
                            )}
                          </div>
                        </div>
                        <Select
                          value={file.subtype}
                          onValueChange={(value) =>
                            updateFile(file.fileId, { subtype: value })
                          }
                        >
                          <SelectTrigger className="w-[140px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {subtypes.map((st) => (
                              <SelectItem key={st} value={st}>
                                {st}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(file.fileId)}
                        >
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Categories */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Categories</CardTitle>
                <CardDescription>
                  Organize files into content categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-3 flex-wrap">
                  {subtypes.map((st) => (
                    <Badge key={st} variant="default" className="text-sm px-3 py-1">
                      {st}
                    </Badge>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={newSubtype}
                    onChange={(e) => setNewSubtype(e.target.value)}
                    placeholder="New category"
                    onKeyPress={(e) => e.key === "Enter" && handleAddSubtype()}
                  />
                  <Button onClick={handleAddSubtype} size="md">
                    <Plus className="w-4 h-4 mr-2" />
                    Add
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Actions Panel (1 column) */}
          <div className="space-y-6">
            {/* Actions Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={handleAutoDetect}
                  disabled={files.length === 0}
                  variant="secondary"
                  className="w-full justify-start"
                >
                  <Search className="w-4 h-4 mr-2" />
                  Auto-Detect Languages
                </Button>
                <Button
                  onClick={handleExtraction}
                  disabled={!clientName || files.length === 0 || extracting}
                  className="w-full justify-start"
                >
                  {extracting ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4 mr-2" />
                  )}
                  {extracting ? "Extracting..." : "Start Extraction"}
                </Button>
              </CardContent>
            </Card>

            {/* Cost Display */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Cost Estimate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary-700 mb-1">
                  {formatCost(estimatedCost())}
                </div>
                <div className="text-sm text-muted-foreground">
                  {formatTokens(totalTokens())} tokens
                </div>
              </CardContent>
            </Card>

            {/* Progress */}
            {extraction.status === "running" && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-sm font-medium">
                      {extraction.completedSubtypes.length} of{" "}
                      {extraction.totalSubtypes} complete
                    </div>
                    {extraction.currentSubtype && (
                      <div className="text-sm text-primary flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing: {extraction.currentSubtype}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Results */}
            {results && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Results Ready!</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(results).map(([subtype, result]) => (
                      <details key={subtype} className="group">
                        <summary className="cursor-pointer p-3 bg-primary-100 rounded-lg hover:bg-primary-200 transition-colors">
                          <div className="font-medium text-primary-900">
                            {subtype}
                          </div>
                          <div className="text-sm text-primary-700">
                            {result.inputTokens + result.outputTokens} tokens
                          </div>
                        </summary>
                        <div className="mt-2 p-3 bg-muted rounded-lg space-y-2">
                          <details>
                            <summary className="cursor-pointer font-medium text-sm">
                              Client Rules
                            </summary>
                            <pre className="mt-2 text-xs overflow-auto max-h-40 p-2 bg-background rounded">
                              {result.clientRules}
                            </pre>
                          </details>
                          <details>
                            <summary className="cursor-pointer font-medium text-sm">
                              Guidelines
                            </summary>
                            <pre className="mt-2 text-xs overflow-auto max-h-40 p-2 bg-background rounded">
                              {result.guidelines}
                            </pre>
                          </details>
                        </div>
                      </details>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
