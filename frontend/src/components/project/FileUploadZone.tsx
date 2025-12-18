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
    <Card className={cn("transition-all", isDragging && "ring-2 ring-primary shadow-lg scale-[1.02]")}>
      <CardContent className="pt-6">
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className={cn(
            "border-2 border-dashed rounded-xl p-8 text-center transition-all",
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
              "flex flex-col items-center gap-3",
              !(disabled || uploading) && "cursor-pointer"
            )}
          >
            {uploading ? (
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
            ) : (
              <Upload
                className={cn(
                  "w-12 h-12 transition-transform",
                  isDragging ? "text-primary scale-110" : "text-primary-600"
                )}
              />
            )}
            <div>
              <p className="text-primary-700 font-medium text-lg">
                {uploading
                  ? "Uploading files..."
                  : isDragging
                  ? "Drop files here"
                  : "Click to upload or drag files here"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                PDF, DOCX, TXT, MD (max {maxSize}MB per file)
              </p>
            </div>
          </label>
        </div>
      </CardContent>
    </Card>
  );
}
