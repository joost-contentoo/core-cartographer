"use client";

import { DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import { formatCost, formatTokens } from "@/lib/utils";

interface CostDisplayProps {
  totalTokens: number;
  estimatedCost: number;
  minimal?: boolean;
}

export function CostDisplay({ totalTokens, estimatedCost, minimal = false }: CostDisplayProps) {
  if (minimal) {
    return (
      <div className="flex items-center gap-4 text-sm bg-background/50 px-3 py-1.5 rounded-lg border border-border/50">
        <div className="flex items-center gap-1.5 font-medium text-primary-700">
          <DollarSign className="w-4 h-4" />
          {formatCost(estimatedCost)}
        </div>
        <div className="h-4 w-px bg-border" />
        <div className="text-muted-foreground whitespace-nowrap">
          {formatTokens(totalTokens)} tokens
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Cost Estimate
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <div className="text-3xl font-bold text-primary-700">
              {formatCost(estimatedCost)}
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              Estimated extraction cost
            </div>
          </div>
          <div className="pt-3 border-t border-border">
            <div className="text-lg font-semibold text-foreground">
              {formatTokens(totalTokens)}
            </div>
            <div className="text-xs text-muted-foreground">
              Total input tokens
            </div>
          </div>
          <div className="text-xs text-muted-foreground pt-2 border-t border-border">
            Based on Claude Opus 4.5 pricing ($15/1M input tokens). Actual cost may vary based on output length.
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
