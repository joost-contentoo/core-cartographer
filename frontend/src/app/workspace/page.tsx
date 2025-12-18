"use client";

import { useState, useCallback, useEffect } from "react";
import { useProjectStore } from "@/lib/store";
import { api } from "@/lib/api";
import { isSupportedFileType } from "@/lib/utils";
import type { SSEEvent, ExtractionResult } from "@/lib/types";
import {
  FileUploadZone,
  FileList,
  SubtypeManager,
  CostDisplay,
  ExtractionProgress,
  FilePreview,
  SettingsPanel,
} from "@/components/project";
import { ResultsDialog } from "@/components/results";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
} from "@/components/ui";
import { Search, Sparkles, Loader2 } from "lucide-react";

export default function WorkspacePage() {
  const {
    clientName,
    setClientName,
    files,
    addFile,
    updateFile,
    removeFile,
    selectedFileId,
    setSelectedFile,
    subtypes,
    addSubtype,
    removeSubtype,
    settings,
    updateSettings,
    extraction,
    setExtractionProgress,
    setResults,
    results,
    totalTokens,
    estimatedCost,
  } = useProjectStore();

  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState<{ message: string; retry?: () => void } | null>(null);
  const [cancelExtraction, setCancelExtraction] = useState<(() => void) | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [lastUploadedFiles, setLastUploadedFiles] = useState<FileList | null>(null);

  // File upload handler
  const handleFileUpload = useCallback(
    async (fileList: FileList) => {
      if (!fileList || fileList.length === 0) return;

      setLastUploadedFiles(fileList);
      setUploading(true);
      setError(null);

      for (const file of Array.from(fileList)) {
        if (!isSupportedFileType(file.name)) {
          setError({
            message: `Unsupported file type: ${file.name}`,
            retry: () => handleFileUpload(fileList),
          });
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
            setError({
              message: result.error || "Failed to parse file",
              retry: () => handleFileUpload(fileList),
            });
          }
        } catch (err) {
          setError({
            message: err instanceof Error ? err.message : "Upload failed",
            retry: () => handleFileUpload(fileList),
          });
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
      setDetecting(true);
      const result = await api.runAutoDetect(files.map((f) => f.fileId));

      result.files.forEach((detectedFile) => {
        updateFile(detectedFile.file_id, {
          language: detectedFile.language,
          pairId: detectedFile.pair_id,
        });
      });
    } catch (err) {
      setError({
        message: err instanceof Error ? err.message : "Auto-detect failed",
        retry: handleAutoDetect,
      });
    } finally {
      setDetecting(false);
    }
  }, [files, updateFile]);

  // Extraction handler
  const handleExtraction = useCallback(async () => {
    if (!clientName || files.length === 0) {
      setError({
        message: "Please provide a client name and upload files",
      });
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

    const cancel = api.extractWithSSE(
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
            // Use getState() to avoid stale closure issue with rapid SSE events
            const currentState = useProjectStore.getState();
            setExtractionProgress({
              completedSubtypes: [...currentState.extraction.completedSubtypes, event.subtype || ""],
            });
            break;

          case "complete":
            if (event.results) {
              const convertedResults: Record<string, ExtractionResult> = {};
              Object.entries(event.results).forEach(([subtype, result]) => {
                convertedResults[subtype] = {
                  clientRules: result.client_rules,
                  guidelines: result.guidelines,
                  inputTokens: result.input_tokens,
                  outputTokens: result.output_tokens,
                };
              });
              setResults(convertedResults);
              setShowResults(true); // Open results dialog
            }
            setExtractionProgress({
              status: "complete",
              currentSubtype: null,
            });
            setExtracting(false);
            setCancelExtraction(null);
            break;

          case "error":
            setError({
              message: event.message || "Extraction failed",
              retry: handleExtraction,
            });
            setExtractionProgress({
              status: "error",
              error: event.message,
            });
            setExtracting(false);
            setCancelExtraction(null);
            break;
        }
      },
      (err: Error) => {
        setError({
          message: err.message,
          retry: handleExtraction,
        });
        setExtractionProgress({
          status: "error",
          error: err.message,
        });
        setExtracting(false);
        setCancelExtraction(null);
      }
    );

    setCancelExtraction(() => cancel);
  }, [
    clientName,
    files,
    subtypes,
    settings,
    setExtractionProgress,
    setResults,
  ]);

  const handleCancelExtraction = useCallback(() => {
    if (cancelExtraction) {
      cancelExtraction();
      setExtracting(false);
      setExtractionProgress({
        status: "idle",
        currentSubtype: null,
        completedSubtypes: [],
        totalSubtypes: 0,
      });
      setCancelExtraction(null);
    }
  }, [cancelExtraction, setExtractionProgress]);

  // File deletion handler - removes from both frontend and backend
  const handleDeleteFile = useCallback(
    async (fileId: string) => {
      try {
        // Remove from backend cache first
        await api.deleteFile(fileId);
      } catch (err) {
        // Log but don't block UI - file might already be expired from cache
        console.warn("Failed to delete file from backend cache:", err);
      }
      // Always remove from frontend store
      removeFile(fileId);
      if (selectedFileId === fileId) {
        setSelectedFile(null);
      }
    },
    [removeFile, selectedFileId, setSelectedFile]
  );

  // SSE cleanup on component unmount
  useEffect(() => {
    return () => {
      if (cancelExtraction) {
        cancelExtraction();
      }
    };
  }, [cancelExtraction]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Delete key: Delete selected file
      if (e.key === "Delete" && selectedFileId && !extracting) {
        e.preventDefault();
        handleDeleteFile(selectedFileId);
      }

      // Enter key: Start extraction (if not already extracting and conditions are met)
      if (
        e.key === "Enter" &&
        !e.shiftKey &&
        !e.ctrlKey &&
        !e.metaKey &&
        clientName &&
        files.length > 0 &&
        !extracting &&
        // Don't trigger if user is typing in an input
        !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)
      ) {
        e.preventDefault();
        handleExtraction();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedFileId, extracting, clientName, files.length, handleDeleteFile, handleExtraction]);

  const selectedFile = files.find((f) => f.fileId === selectedFileId) || null;

  return (
    <div className="min-h-screen bg-muted/30 p-6 md:p-8">
      <div className="max-w-[1600px] mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col gap-2">
          <div className="flex items-center gap-2 text-primary">
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="font-semibold tracking-tight text-sm uppercase">Core Cartographer</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Workspace
            </h1>
            <p className="text-muted-foreground text-lg max-w-2xl mt-1">
              Extract localization rules and guidelines from your project documentation.
            </p>
          </div>
        </header>

        {/* Error Banner */}
        {error && (
          <Card className="border-destructive/50 bg-destructive/10 animate-in slide-in-from-top-2 duration-300">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <span className="text-destructive text-lg">⚠️</span>
                <div className="flex-1">
                  <p className="text-destructive font-medium">{error.message}</p>
                </div>
                <div className="flex gap-2">
                  {error.retry && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setError(null);
                        error.retry?.();
                      }}
                    >
                      Retry
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setError(null)}
                    className="hover:bg-destructive/10 hover:text-destructive"
                  >
                    ✕
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Bar: Project Setup & Actions */}
        <Card className="border-none shadow-md">
          <CardContent className="py-4">
            <div className="flex flex-wrap items-center gap-4 md:gap-6">
              {/* Client Name Input */}
              <div className="flex items-center gap-2 flex-1 min-w-[200px] max-w-[300px]">
                <Label htmlFor="client-name" className="text-sm whitespace-nowrap">Client</Label>
                <Input
                  id="client-name"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="e.g., Acme Corporation"
                  className="h-9"
                />
              </div>

              {/* Cost Display */}
              <CostDisplay
                totalTokens={totalTokens()}
                estimatedCost={estimatedCost()}
                minimal={true}
              />

              {/* Spacer */}
              <div className="flex-1" />

              {/* Primary Actions */}
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleAutoDetect}
                  disabled={files.length === 0 || detecting}
                  variant="secondary"
                  size="sm"
                  className="h-9"
                >
                  {detecting ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4 mr-2" />
                  )}
                  {detecting ? "Detecting..." : "Auto-Detect"}
                </Button>
                <Button
                  onClick={handleExtraction}
                  disabled={!clientName || files.length === 0 || extracting}
                  size="sm"
                  className="h-9"
                >
                  {extracting ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4 mr-2" />
                  )}
                  {extracting ? "Extracting..." : "Start Extraction"}
                </Button>
                <SettingsPanel settings={settings} onUpdate={updateSettings} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content: Document Table (Central) + Preview (Side) */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">

          {/* MAIN: Document Table - Takes most space */}
          <div className="xl:col-span-8 space-y-4">
            {/* Upload Zone */}
            <FileUploadZone
              onFilesSelected={handleFileUpload}
              uploading={uploading}
              disabled={uploading}
            />

            {/* Document Table - THE CORE */}
            <Card className="border shadow-sm overflow-hidden">
              <CardHeader className="py-3 px-4 bg-muted/30 border-b">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold">
                    Documents
                  </CardTitle>
                  <SubtypeManager
                    subtypes={subtypes}
                    onAddSubtype={addSubtype}
                    onRemoveSubtype={removeSubtype}
                    disabled={extracting}
                    compact={true}
                  />
                </div>
              </CardHeader>
              <FileList
                files={files}
                subtypes={subtypes}
                selectedFileId={selectedFileId}
                onSelectFile={setSelectedFile}
                onUpdateFile={updateFile}
                onDeleteFile={handleDeleteFile}
              />
            </Card>

            {/* Results Banner (when available) */}
            {results && (
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                      <Sparkles className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="font-medium text-foreground">Extraction Complete</div>
                      <div className="text-sm text-muted-foreground">
                        {Object.keys(results).length} categories processed
                      </div>
                    </div>
                  </div>
                  <Button onClick={() => setShowResults(true)}>
                    View Results
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* SIDE: Preview Panel */}
          <div className="xl:col-span-4 xl:sticky xl:top-8 h-fit">
            <Card className="overflow-hidden">
              <CardHeader className="py-3 px-4 bg-muted/30 border-b">
                <CardTitle className="text-base font-semibold truncate">
                  {selectedFile ? selectedFile.filename : "Preview"}
                </CardTitle>
              </CardHeader>
              <div className="h-[500px] xl:h-[calc(100vh-16rem)]">
                <FilePreview file={selectedFile} className="h-full w-full" />
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Extraction Progress Modal */}
      <ExtractionProgress
        progress={extraction}
        subtypes={subtypes}
        onCancel={extracting ? handleCancelExtraction : undefined}
      />

      {/* Results Dialog */}
      <ResultsDialog
        results={results}
        open={showResults}
        onOpenChange={setShowResults}
      />
    </div>
  );
}
// End of component
