"use client";

import { useEffect, useState } from "react";
import { Loader2, CheckCircle, Circle, XCircle, Clock } from "lucide-react";
import { ExtractionProgress as ExtractionProgressType } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Button,
  Progress,
} from "@/components/ui";
import { cn } from "@/lib/utils";

interface ExtractionProgressProps {
  progress: ExtractionProgressType;
  subtypes: string[];
  onCancel?: () => void;
}

export function ExtractionProgress({
  progress,
  subtypes,
  onCancel,
}: ExtractionProgressProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const isOpen = progress.status === "running";

  useEffect(() => {
    if (progress.status === "running") {
      setElapsedSeconds(0);
      const interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [progress.status]);

  const progressPercentage =
    progress.totalSubtypes > 0
      ? (progress.completedSubtypes.length / progress.totalSubtypes) * 100
      : 0;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getSubtypeStatus = (subtype: string) => {
    if (progress.completedSubtypes.includes(subtype)) {
      return "completed";
    } else if (progress.currentSubtype === subtype) {
      return "processing";
    } else {
      return "pending";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl">Extracting Rules & Guidelines</DialogTitle>
          <DialogDescription>
            Processing your documentation files with Claude AI
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Overall Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Overall Progress</span>
              <span className="text-muted-foreground">
                {progress.completedSubtypes.length} of {progress.totalSubtypes} complete
              </span>
            </div>
            <Progress value={progressPercentage} className="h-3" />
            <div className="text-right">
              <span className="text-lg font-semibold text-primary">
                {Math.round(progressPercentage)}%
              </span>
            </div>
          </div>

          {/* Category Status */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Categories:</div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {subtypes.map((subtype) => {
                const status = getSubtypeStatus(subtype);
                return (
                  <div
                    key={subtype}
                    className={cn(
                      "flex items-center gap-3 p-2 rounded-lg transition-colors",
                      status === "processing" && "bg-primary-50 dark:bg-primary-900/20",
                      status === "completed" && "bg-muted"
                    )}
                  >
                    {status === "completed" && (
                      <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
                    )}
                    {status === "processing" && (
                      <Loader2 className="w-5 h-5 text-primary animate-spin shrink-0" />
                    )}
                    {status === "pending" && (
                      <Circle className="w-5 h-5 text-muted-foreground shrink-0" />
                    )}
                    <span className={cn(
                      "font-medium flex-1",
                      status === "completed" && "text-muted-foreground",
                      status === "processing" && "text-primary"
                    )}>
                      {subtype}
                    </span>
                    {status === "processing" && (
                      <span className="text-xs text-primary">Processing...</span>
                    )}
                    {status === "completed" && (
                      <span className="text-xs text-green-600">Done</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Time Elapsed */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground border-t pt-4">
            <Clock className="w-4 h-4" />
            <span>Time elapsed: {formatTime(elapsedSeconds)}</span>
          </div>

          {/* Error Display */}
          {progress.status === "error" && progress.error && (
            <div className="p-3 bg-destructive/10 border border-destructive rounded-lg">
              <div className="flex items-start gap-2">
                <XCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                <div>
                  <div className="font-medium text-destructive">Extraction Failed</div>
                  <div className="text-sm text-destructive/80 mt-1">{progress.error}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Cancel Button */}
        {onCancel && progress.status === "running" && (
          <div className="flex justify-end">
            <Button variant="secondary" onClick={onCancel}>
              Cancel Extraction
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
