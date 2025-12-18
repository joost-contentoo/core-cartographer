"use client";

import { FileText } from "lucide-react";
import { FileMetadata } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import { FileItem } from "./FileItem";

interface FileListProps {
  files: FileMetadata[];
  subtypes: string[];
  selectedFileId?: string | null;
  onSelectFile?: (fileId: string) => void;
  onUpdateFile: (fileId: string, updates: Partial<FileMetadata>) => void;
  onDeleteFile: (fileId: string) => void;
}

export function FileList({
  files,
  subtypes,
  selectedFileId,
  onSelectFile,
  onUpdateFile,
  onDeleteFile,
}: FileListProps) {
  if (files.length === 0) {
    return null;
  }

  const handleUpdateSubtype = (fileId: string, subtype: string) => {
    onUpdateFile(fileId, { subtype });
  };

  return (
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
            <FileItem
              key={file.fileId}
              file={file}
              subtypes={subtypes}
              isSelected={selectedFileId === file.fileId}
              onSelect={onSelectFile}
              onUpdateSubtype={handleUpdateSubtype}
              onDelete={onDeleteFile}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
