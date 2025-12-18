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

  // Helper function to get badge color for each subtype
  const getBadgeColor = (subtype: string, index: number) => {
    const colors = [
      "bg-blue-100 text-blue-700 border-blue-200",
      "bg-purple-100 text-purple-700 border-purple-200",
      "bg-pink-100 text-pink-700 border-pink-200",
      "bg-orange-100 text-orange-700 border-orange-200",
      "bg-teal-100 text-teal-700 border-teal-200",
      "bg-indigo-100 text-indigo-700 border-indigo-200",
      "bg-cyan-100 text-cyan-700 border-cyan-200",
      "bg-emerald-100 text-emerald-700 border-emerald-200",
    ];
    return colors[index % colors.length];
  };

  // Compact mode: inline badges with small add button
  if (compact) {
    return (
      <>
        <div className="flex items-center gap-2 flex-wrap">
          {subtypes.map((st, index) => (
            <Badge
              key={st}
              variant="outline"
              className={`text-xs px-2.5 py-1 flex items-center gap-1.5 font-medium ${getBadgeColor(st, index)}`}
            >
              {st}
              {canDeleteSubtype(st) && !disabled && (
                <button
                  onClick={() => setDeleteTarget(st)}
                  className="hover:bg-black/10 rounded-full p-0.5 transition-colors"
                  aria-label={`Remove ${st}`}
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </Badge>
          ))}
          {showAddInput ? (
            <div className="flex items-center gap-1.5">
              <Input
                value={newSubtype}
                onChange={(e) => setNewSubtype(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Category name"
                disabled={disabled}
                className="h-7 w-[140px] text-xs"
                autoFocus
              />
              <Button
                onClick={handleAdd}
                disabled={disabled || !newSubtype.trim()}
                size="sm"
                className="h-7 px-3 text-xs bg-green-600 hover:bg-green-700 text-white"
              >
                Add
              </Button>
            </div>
          ) : (
            <Button
              onClick={() => setShowAddInput(true)}
              disabled={disabled}
              size="sm"
              className="h-7 px-3 text-xs bg-green-600 hover:bg-green-700 text-white font-semibold shadow-sm"
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

  // Full mode: Compact inline version
  return (
    <>
      <div className="space-y-2">
        {/* Existing Subtypes */}
        <div className="flex gap-2 flex-wrap">
          {subtypes.map((st, index) => (
            <Badge
              key={st}
              variant="outline"
              className={`text-xs px-2.5 py-1 flex items-center gap-1.5 font-medium ${getBadgeColor(st, index)}`}
            >
              {st}
              {canDeleteSubtype(st) && !disabled && (
                <button
                  onClick={() => setDeleteTarget(st)}
                  className="hover:bg-black/10 rounded-full p-0.5 transition-colors"
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
            onKeyDown={handleKeyPress}
            placeholder="Add category (e.g., legal, marketing)"
            disabled={disabled}
            className="h-8 text-sm"
          />
          <Button
            onClick={handleAdd}
            disabled={disabled || !newSubtype.trim()}
            size="sm"
            className="h-8 px-3 text-xs bg-green-600 hover:bg-green-700 text-white font-semibold"
          >
            <Plus className="w-3 h-3 mr-1" />
            Add
          </Button>
        </div>
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
