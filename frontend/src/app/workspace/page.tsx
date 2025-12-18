"use client";

import { useState, useCallback, useEffect } from "react";
import { useProjectStore } from "@/lib/store";
import { api } from "@/lib/api";
import { isSupportedFileType } from "@/lib/utils";
import type { SSEEvent } from "@/lib/api";
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
    extraction.completedSubtypes,
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

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Delete key: Delete selected file
      if (e.key === "Delete" && selectedFileId && !extracting) {
        e.preventDefault();
        removeFile(selectedFileId);
        setSelectedFile(null);
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
  }, [selectedFileId, extracting, clientName, files.length, removeFile, setSelectedFile, handleExtraction]);

  const selectedFile = files.find((f) => f.fileId === selectedFileId) || null;

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
          <Card className="mb-6 border-destructive bg-destructive/10 animate-in slide-in-from-top-2 duration-300">
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
                  >
                    ✕
                  </Button>
                </div>
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
            <FileUploadZone
              onFilesSelected={handleFileUpload}
              uploading={uploading}
              disabled={uploading}
            />

            {/* File List */}
            <FileList
              files={files}
              subtypes={subtypes}
              selectedFileId={selectedFileId}
              onSelectFile={setSelectedFile}
              onUpdateFile={updateFile}
              onDeleteFile={removeFile}
            />

            {/* Categories */}
            <SubtypeManager
              subtypes={subtypes}
              onAddSubtype={addSubtype}
              onRemoveSubtype={removeSubtype}
              disabled={extracting}
            />
          </div>

          {/* Right Panel (1 column) */}
          <div className="space-y-6">
            {/* Actions Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <SettingsPanel settings={settings} onUpdate={updateSettings} />
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
            <CostDisplay
              totalTokens={totalTokens()}
              estimatedCost={estimatedCost()}
            />

            {/* File Preview */}
            <FilePreview file={selectedFile} />

            {/* Results Available */}
            {results && (
              <Card className="border-green-200 bg-green-50 dark:bg-green-900/10 animate-in slide-in-from-bottom-4 duration-500">
                <CardContent className="pt-6">
                  <div className="text-center space-y-3">
                    <div className="text-2xl animate-in zoom-in duration-500 delay-100">✨</div>
                    <div>
                      <div className="font-semibold text-green-900 dark:text-green-100">
                        Extraction Complete!
                      </div>
                      <div className="text-sm text-green-700 dark:text-green-300 mt-1">
                        {Object.keys(results).length} {Object.keys(results).length === 1 ? "category" : "categories"} processed
                      </div>
                    </div>
                    <Button
                      onClick={() => setShowResults(true)}
                      className="w-full"
                    >
                      View Results
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
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
