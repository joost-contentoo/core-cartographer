"use client";

import { useState } from "react";
import { Plus, X, AlertTriangle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Button,
  Badge,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui";

interface SubtypeManagerProps {
  subtypes: string[];
  onAddSubtype: (subtype: string) => void;
  onRemoveSubtype: (subtype: string) => void;
  disabled?: boolean;
  compact?: boolean;
}

export function SubtypeManager({
  subtypes,
  onAddSubtype,
  onRemoveSubtype,
  disabled = false,
  compact = false,
}: SubtypeManagerProps) {
  const [newSubtype, setNewSubtype] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [showAddInput, setShowAddInput] = useState(false);

  const handleAdd = () => {
    const trimmed = newSubtype.trim().toLowerCase();
    if (trimmed && !subtypes.includes(trimmed)) {
      onAddSubtype(trimmed);
      setNewSubtype("");
      setShowAddInput(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleAdd();
    }
    if (e.key === "Escape") {
      setShowAddInput(false);
      setNewSubtype("");
    }
  };

  const handleDelete = () => {
    if (deleteTarget) {
      onRemoveSubtype(deleteTarget);
      setDeleteTarget(null);
    }
  };

  const canDeleteSubtype = (subtype: string) => {
    // Prevent deletion of 'general' subtype
    return subtype !== "general";
  };

  // Compact mode: inline badges with small add button
  if (compact) {
    return (
      <>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground mr-1">Categories:</span>
          {subtypes.map((st) => (
            <Badge
              key={st}
              variant="secondary"
              className="text-xs px-2 py-0.5 flex items-center gap-1"
            >
              {st}
              {canDeleteSubtype(st) && !disabled && (
                <button
                  onClick={() => setDeleteTarget(st)}
                  className="hover:bg-muted rounded-full p-0.5 transition-colors"
                  aria-label={`Remove ${st}`}
                >
                  <X className="w-2.5 h-2.5" />
                </button>
              )}
            </Badge>
          ))}
          {showAddInput ? (
            <div className="flex items-center gap-1">
              <Input
                value={newSubtype}
                onChange={(e) => setNewSubtype(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Category name"
                disabled={disabled}
                className="h-6 w-[120px] text-xs"
                autoFocus
              />
              <Button
                onClick={handleAdd}
                disabled={disabled || !newSubtype.trim()}
                size="sm"
                className="h-6 px-2 text-xs"
              >
                Add
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => setShowAddInput(true)}
              disabled={disabled}
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs"
            >
              <Plus className="w-3 h-3 mr-1" />
              Add
            </Button>
          )}
        </div>

        {/* Delete Confirmation Dialog */}
        <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-destructive" />
                Remove Category?
              </DialogTitle>
              <DialogDescription>
                Are you sure you want to remove the <strong>{deleteTarget}</strong> category?
                Files in this category will be moved to <strong>general</strong>.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={handleDelete}>
                Remove
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </>
    );
  }

  // Full mode: Card with description
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Categories</CardTitle>
          <CardDescription>
            Organize files into content categories. Files will be processed separately by category.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Existing Subtypes */}
          <div className="flex gap-2 flex-wrap">
            {subtypes.map((st) => (
              <Badge
                key={st}
                variant="default"
                className="text-sm px-3 py-1.5 flex items-center gap-2"
              >
                {st}
                {canDeleteSubtype(st) && !disabled && (
                  <button
                    onClick={() => setDeleteTarget(st)}
                    className="hover:bg-primary-600 rounded-full p-0.5 transition-colors"
                    aria-label={`Remove ${st}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </Badge>
            ))}
          </div>

          {/* Add New Subtype */}
          <div className="flex gap-2">
            <Input
              value={newSubtype}
              onChange={(e) => setNewSubtype(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Add new category (e.g., legal, marketing)"
              disabled={disabled}
            />
            <Button
              onClick={handleAdd}
              disabled={disabled || !newSubtype.trim()}
              size="md"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add
            </Button>
          </div>

          {subtypes.length > 1 && (
            <p className="text-xs text-muted-foreground">
              Tip: Each category will be extracted separately, allowing you to organize different types of content.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              Remove Category?
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to remove the <strong>{deleteTarget}</strong> category?
              Files in this category will be moved to <strong>general</strong>.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="secondary"
              onClick={() => setDeleteTarget(null)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
            >
              Remove
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
