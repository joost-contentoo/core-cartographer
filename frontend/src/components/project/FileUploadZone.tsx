"use client";

import { useCallback, useState, DragEvent } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  onFilesSelected: (files: FileList) => void;
  uploading?: boolean;
  disabled?: boolean;
  accept?: string;
  maxSize?: number; // in MB
}

export function FileUploadZone({
  onFilesSelected,
  uploading = false,
  disabled = false,
  accept = ".pdf,.docx,.txt,.md",
  maxSize = 10,
}: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && !uploading) {
      setIsDragging(true);
    }
  }, [disabled, uploading]);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set dragging to false if we're leaving the container entirely
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled || uploading) return;

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        onFilesSelected(files);
      }
    },
    [disabled, uploading, onFilesSelected]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        onFilesSelected(files);
      }
      // Reset input so the same file can be selected again
      e.target.value = "";
    },
    [onFilesSelected]
  );

  return (
    <Card className={cn("transition-all h-full", isDragging && "ring-2 ring-primary shadow-lg scale-[1.01]")}>
      <CardContent className="pt-3 pb-3 h-full">
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-lg p-4 text-center transition-all h-full flex items-center justify-center",
            isDragging
              ? "border-primary bg-primary-50 dark:bg-primary-900/20"
              : "border-primary-300 hover:border-primary-500 hover:bg-primary-50/50",
            (disabled || uploading) && "opacity-50 cursor-not-allowed"
          )}
        >
          <input
            type="file"
            multiple
            accept={accept}
            onChange={handleFileInput}
            className="hidden"
            id="file-upload-input"
            disabled={disabled || uploading}
          />
          <label
            htmlFor="file-upload-input"
            className={cn(
              "flex flex-col items-center gap-2",
              !(disabled || uploading) && "cursor-pointer"
            )}
          >
            {uploading ? (
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            ) : (
              <Upload
                className={cn(
                  "w-8 h-8 transition-transform",
                  isDragging ? "text-primary scale-110" : "text-primary-600"
                )}
              />
            )}
            <div>
              <p className="text-primary-700 font-medium text-sm">
                {uploading
                  ? "Uploading files..."
                  : isDragging
                  ? "Drop files here"
                  : "Click to upload or drag files here"}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                PDF, DOCX, TXT, MD (max {maxSize}MB per file)
              </p>
            </div>
          </label>
        </div>
      </CardContent>
    </Card>
  );
}
