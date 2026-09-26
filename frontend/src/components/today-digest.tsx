"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";
import type { Digest, DigestItem } from "@/lib/types";
import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const SECTION_LABELS: Record<string, string> = {
  top_story: "🔥 Top Stories",
  category: "📡 Developments",
  worth_exploring: "⭐ Worth Exploring",
  learning: "📚 One Thing To Learn",
};

const ACTION_VARIANTS: Record<string, "default" | "secondary" | "destructive"> = {
  investigate: "default",
  bookmark: "secondary",
  ignore: "destructive",
};

export function TodayDigest() {
  const [digest, setDigest] = useState<Digest | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setDigest(await api<Digest>("/api/digests/today"));
      } catch {
        setDigest(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const regenerate = async () => {
    setRegenerating(true);
    try {
      const next = await api<Digest>("/api/digests/today/regenerate", { method: "POST" });
      setDigest(next);
      toast.success("Digest regenerated");
    } catch {
      toast.error("Could not regenerate — is the backend running with data?");
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading digest…</p>;
  }

  if (!digest) {
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-3 pt-6">
          <p className="text-sm text-muted-foreground">
            No digest for today yet. Run the pipeline or collect some sources first.
          </p>
          <Button onClick={regenerate} disabled={regenerating}>
            <RefreshCw className="size-4" />
            {regenerating ? "Generating…" : "Generate now"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const sections: { key: string; items: DigestItem[] }[] = [];
  for (const item of digest.items) {
    const last = sections[sections.length - 1];
    if (last && last.key === item.section) {
      last.items.push(item);
    } else {
      sections.push({ key: item.section, items: [item] });
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span>{digest.digest_date}</span>
          <Badge variant="secondary">{digest.status}</Badge>
          <span>⏱ ~{digest.reading_time_minutes} min read</span>
          <span>
            {digest.items.length} item{digest.items.length === 1 ? "" : "s"}
          </span>
        </div>
        <Button variant="outline" size="sm" onClick={regenerate} disabled={regenerating}>
          <RefreshCw className="size-4" />
          {regenerating ? "Regenerating…" : "Regenerate"}
        </Button>
      </div>

      {sections.map((section) => (
        <div key={section.key} className="space-y-4">
          <h2 className="pt-2 text-sm font-semibold tracking-wide text-muted-foreground uppercase">
            {SECTION_LABELS[section.key] ?? section.key}
          </h2>
          {section.items.map((item) => (
            <DigestCard key={item.id} item={item} />
          ))}
        </div>
      ))}
    </div>
  );
}

function DigestCard({ item }: { item: DigestItem }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <CardTitle className="text-base leading-snug">
            <a href={item.url} target="_blank" rel="noreferrer" className="hover:underline">
              {item.title}
            </a>
          </CardTitle>
          <Badge variant={ACTION_VARIANTS[item.recommended_action] ?? "secondary"}>
            {item.recommended_action}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">
          {item.category ?? "Uncategorized"} · via {item.source_name ?? "unknown"}
        </p>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p>{item.summary}</p>
        {item.why_it_matters && (
          <p>
            <span className="font-medium">Why it matters:</span> {item.why_it_matters}
          </p>
        )}
        {item.why_user_should_care && (
          <p>
            <span className="font-medium">Why you should care:</span> {item.why_user_should_care}
          </p>
        )}
        <Separator />
        <a
          href={item.url}
          target="_blank"
          rel="noreferrer"
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          Read original ↗
        </a>
      </CardContent>
    </Card>
  );
}
