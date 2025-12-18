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
        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center animate-in fade-in duration-300">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center mb-4 animate-in zoom-in duration-500 delay-100">
              <FileText className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="font-semibold text-lg mb-2 animate-in slide-in-from-bottom-2 duration-500 delay-200">No files uploaded yet</h3>
            <p className="text-sm text-muted-foreground max-w-sm animate-in slide-in-from-bottom-2 duration-500 delay-300">
              Upload your documentation files above to get started. Supported formats include PDF, DOCX, and TXT.
            </p>
          </div>
        ) : (
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
        )}
      </CardContent>
    </Card>
  );
}
