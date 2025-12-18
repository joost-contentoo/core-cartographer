"use client";

import { useState } from "react";
import { FileText, Trash2, AlertTriangle } from "lucide-react";
import { FileMetadata } from "@/lib/types";
import { formatTokens, cn } from "@/lib/utils";
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

interface FileItemProps {
  file: FileMetadata;
  subtypes: string[];
  isSelected?: boolean;
  onSelect?: (fileId: string) => void;
  onUpdateSubtype: (fileId: string, subtype: string) => void;
  onDelete: (fileId: string) => void;
}

export function FileItem({
  file,
  subtypes,
  isSelected = false,
  onSelect,
  onUpdateSubtype,
  onDelete,
}: FileItemProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleDelete = () => {
    onDelete(file.fileId);
    setShowDeleteDialog(false);
  };

  const handleClick = () => {
    if (onSelect) {
      onSelect(file.fileId);
    }
  };

  return (
    <>
      <div
        onClick={handleClick}
        className={cn(
          "flex items-center gap-3 p-3 rounded-lg transition-all",
          "border border-transparent",
          isSelected
            ? "bg-primary-100 dark:bg-primary-900/30 border-primary-300"
            : "bg-muted hover:bg-muted/80",
          onSelect && "cursor-pointer"
        )}
      >
        <FileText className="w-5 h-5 text-primary shrink-0" />

        <div className="flex-1 min-w-0">
          <div className="font-medium truncate" title={file.filename}>
            {file.filename}
          </div>
          <div className="text-sm text-muted-foreground flex items-center gap-2 flex-wrap mt-1">
            <Badge variant="secondary" className="text-xs">
              {file.language.toUpperCase()}
            </Badge>
            <span className="text-xs">{formatTokens(file.tokens)} tokens</span>
            {file.pairId && (
              <Badge variant="outline" className="text-xs">
                Pair #{file.pairId}
              </Badge>
            )}
            {file.status === "uploading" && (
              <Badge variant="secondary" className="text-xs">
                Uploading...
              </Badge>
            )}
            {file.status === "error" && (
              <Badge variant="destructive" className="text-xs">
                Error
              </Badge>
            )}
          </div>
          {file.error && (
            <div className="text-xs text-destructive mt-1">{file.error}</div>
          )}
        </div>

        <Select
          value={file.subtype}
          onValueChange={(value) => onUpdateSubtype(file.fileId, value)}
          disabled={file.status === "uploading"}
        >
          <SelectTrigger
            className="w-[140px]"
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

        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            setShowDeleteDialog(true);
          }}
          disabled={file.status === "uploading"}
          className="shrink-0"
        >
          <Trash2 className="w-4 h-4 text-destructive" />
        </Button>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              Delete File?
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to remove <strong>{file.filename}</strong>?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="secondary"
              onClick={() => setShowDeleteDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
