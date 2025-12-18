"use client";

import { useState, useMemo } from "react";
import { FileText, Trash2, AlertTriangle, Link2 } from "lucide-react";
import { FileMetadata } from "@/lib/types";
import { formatTokens, cn, LANGUAGES, getLanguageInfo } from "@/lib/utils";
import {
  Badge,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui";

interface FileListProps {
  files: FileMetadata[];
  subtypes: string[];
  selectedFileId?: string | null;
  onSelectFile?: (fileId: string) => void;
  onUpdateFile: (fileId: string, updates: Partial<FileMetadata>) => void;
  onDeleteFile: (fileId: string) => void;
  compact?: boolean;
}

export function FileList({
  files,
  subtypes,
  selectedFileId,
  onSelectFile,
  onUpdateFile,
  onDeleteFile,
}: FileListProps) {
  const [deleteTarget, setDeleteTarget] = useState<FileMetadata | null>(null);

  // Sort files by pairId, then by filename within each pair
  const sortedFiles = useMemo(() => {
    return [...files].sort((a, b) => {
      // Files with pairId come first, sorted by pairId
      if (a.pairId && b.pairId) {
        if (a.pairId !== b.pairId) return a.pairId.localeCompare(b.pairId);
        // Within same pair, sort by language (source language first typically)
        return a.language.localeCompare(b.language);
      }
      if (a.pairId && !b.pairId) return -1;
      if (!a.pairId && b.pairId) return 1;
      // Unpaired files sorted by filename
      return a.filename.localeCompare(b.filename);
    });
  }, [files]);

  // Group files by pairId for visual separation
  const groupedFiles = useMemo(() => {
    const groups: { pairId: string | null; files: FileMetadata[] }[] = [];
    let currentPairId: string | null | undefined = undefined;

    sortedFiles.forEach((file) => {
      if (file.pairId !== currentPairId) {
        groups.push({ pairId: file.pairId, files: [file] });
        currentPairId = file.pairId;
      } else {
        groups[groups.length - 1].files.push(file);
      }
    });

    return groups;
  }, [sortedFiles]);

  const handleDelete = () => {
    if (deleteTarget) {
      onDeleteFile(deleteTarget.fileId);
      setDeleteTarget(null);
    }
  };

  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <FileText className="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 className="font-semibold text-lg mb-2">No documents yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Upload your documents above to get started.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                Document
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground w-[140px]">
                Language
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground w-[100px]">
                Pair
              </th>
              <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground w-[150px]">
                Category
              </th>
              <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground w-[80px]">
                Tokens
              </th>
              <th className="w-[50px]"></th>
            </tr>
          </thead>
          <tbody>
            {groupedFiles.map((group, groupIndex) => (
              group.files.map((file, fileIndex) => {
                const langInfo = getLanguageInfo(file.language);
                const isFirstInPair = fileIndex === 0 && group.pairId;
                const isSelected = selectedFileId === file.fileId;

                return (
                  <tr
                    key={file.fileId}
                    onClick={() => onSelectFile?.(file.fileId)}
                    className={cn(
                      "border-b transition-colors",
                      isSelected
                        ? "bg-primary/10 border-primary/20"
                        : "hover:bg-muted/30",
                      onSelectFile && "cursor-pointer",
                      // Add visual grouping for pairs
                      group.pairId && fileIndex === 0 && groupIndex > 0 && "border-t-2 border-t-muted"
                    )}
                  >
                    {/* Document name */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                        <div className="min-w-0">
                          <div className="font-medium truncate max-w-[300px]" title={file.filename}>
                            {file.filename}
                          </div>
                          {file.status === "error" && file.error && (
                            <div className="text-xs text-destructive mt-0.5">{file.error}</div>
                          )}
                        </div>
                        {file.status === "uploading" && (
                          <Badge variant="secondary" className="text-xs shrink-0">
                            Uploading...
                          </Badge>
                        )}
                        {file.status === "error" && (
                          <Badge variant="destructive" className="text-xs shrink-0">
                            Error
                          </Badge>
                        )}
                      </div>
                    </td>

                    {/* Language selector - PROMINENT */}
                    <td className="py-3 px-4">
                      <Select
                        value={file.language}
                        onValueChange={(value) => onUpdateFile(file.fileId, { language: value })}
                        disabled={file.status === "uploading"}
                      >
                        <SelectTrigger
                          className="w-[130px] h-9"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <SelectValue>
                            <span className="flex items-center gap-2">
                              <span className="text-lg">{langInfo.flag}</span>
                              <span>{langInfo.code.toUpperCase()}</span>
                            </span>
                          </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                          {LANGUAGES.map((lang) => (
                            <SelectItem key={lang.code} value={lang.code}>
                              <span className="flex items-center gap-2">
                                <span className="text-lg">{lang.flag}</span>
                                <span>{lang.name}</span>
                              </span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>

                    {/* Pair indicator */}
                    <td className="py-3 px-4">
                      {file.pairId ? (
                        <Badge
                          variant="outline"
                          className={cn(
                            "font-mono text-sm",
                            isFirstInPair && "border-primary text-primary"
                          )}
                        >
                          <Link2 className="w-3 h-3 mr-1" />
                          {file.pairId}
                        </Badge>
                      ) : (
                        <span className="text-sm text-muted-foreground">—</span>
                      )}
                    </td>

                    {/* Category/Subtype selector */}
                    <td className="py-3 px-4">
                      <Select
                        value={file.subtype}
                        onValueChange={(value) => onUpdateFile(file.fileId, { subtype: value })}
                        disabled={file.status === "uploading"}
                      >
                        <SelectTrigger
                          className="w-[140px] h-9"
                          onClick={(e) => e.stopPropagation()}
                        >
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
                    </td>

                    {/* Token count */}
                    <td className="py-3 px-4 text-right">
                      <span className="text-sm text-muted-foreground tabular-nums">
                        {formatTokens(file.tokens)}
                      </span>
                    </td>

                    {/* Delete button */}
                    <td className="py-3 px-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteTarget(file);
                        }}
                        disabled={file.status === "uploading"}
                        className="h-8 w-8 p-0 opacity-50 hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                );
              })
            ))}
          </tbody>
        </table>
      </div>

      {/* File count summary */}
      <div className="px-4 py-3 border-t bg-muted/30 text-sm text-muted-foreground flex items-center justify-between">
        <span>{files.length} document{files.length !== 1 ? 's' : ''}</span>
        {groupedFiles.filter(g => g.pairId).length > 0 && (
          <span className="flex items-center gap-1">
            <Link2 className="w-3 h-3" />
            {groupedFiles.filter(g => g.pairId).length} pair{groupedFiles.filter(g => g.pairId).length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              Delete Document?
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to remove <strong>{deleteTarget?.filename}</strong>?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
