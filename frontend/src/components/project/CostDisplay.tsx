"use client";

import { DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import { formatCost, formatTokens } from "@/lib/utils";

interface CostDisplayProps {
  totalTokens: number;
  estimatedCost: number;
}

export function CostDisplay({ totalTokens, estimatedCost }: CostDisplayProps) {
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
