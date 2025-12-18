"use client";

import { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";
import { Settings, AVAILABLE_MODELS } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Button,
  Card,
  CardContent,
  Label,
} from "@/components/ui";

interface SettingsPanelProps {
  settings: Settings;
  onUpdate: (settings: Partial<Settings>) => void;
}

export function SettingsPanel({ settings, onUpdate }: SettingsPanelProps) {
  const [open, setOpen] = useState(false);
  const [localSettings, setLocalSettings] = useState<Settings>(settings);

  const handleSave = () => {
    onUpdate(localSettings);
    setOpen(false);
  };

  const handleCancel = () => {
    setLocalSettings(settings); // Reset to original
    setOpen(false);
  };

  // Use centralized model list from types.ts
  const models = AVAILABLE_MODELS;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" className="w-full justify-start">
          <SettingsIcon className="w-4 h-4 mr-2" />
          Settings
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Extraction Settings
          </DialogTitle>
          <DialogDescription>
            Configure how your documents are processed
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Processing Mode */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Processing Mode</Label>
            <div className="space-y-2">
              <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted transition-colors">
                <input
                  type="radio"
                  name="processing-mode"
                  checked={!localSettings.batchProcessing}
                  onChange={() =>
                    setLocalSettings({ ...localSettings, batchProcessing: false })
                  }
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Individual</div>
                  <div className="text-sm text-muted-foreground">
                    One API call per category. Slower but better for testing.
                  </div>
                </div>
              </label>
              <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted transition-colors">
                <input
                  type="radio"
                  name="processing-mode"
                  checked={localSettings.batchProcessing}
                  onChange={() =>
                    setLocalSettings({ ...localSettings, batchProcessing: true })
                  }
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Batch (Recommended)</div>
                  <div className="text-sm text-muted-foreground">
                    Single API call for all categories. Faster and more efficient.
                  </div>
                </div>
              </label>
            </div>
          </div>

          {/* Model Selection */}
          <div className="space-y-3">
            <Label htmlFor="model-select" className="text-base font-semibold">
              Model
            </Label>
            <select
              id="model-select"
              value={localSettings.model}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, model: e.target.value })
              }
              className="w-full px-3 py-2 border border-border rounded-lg bg-background"
            >
              {models.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              Claude Opus 4.5 provides the best results for complex extractions.
            </p>
          </div>

          {/* Debug Mode */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Debug Mode</Label>
            <label className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-muted transition-colors">
              <input
                type="checkbox"
                checked={localSettings.debugMode}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, debugMode: e.target.checked })
                }
                className="mt-1"
              />
              <div className="flex-1">
                <div className="font-medium">Save prompts to disk</div>
                <div className="text-sm text-muted-foreground">
                  Saves prompts without making API calls. Useful for testing prompt templates.
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave}>Save Settings</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
