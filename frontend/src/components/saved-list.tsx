"use client";

import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { SavedItem } from "@/lib/types";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export function SavedList() {
  const [items, setItems] = useState<SavedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setItems(await api<SavedItem[]>("/api/feedback/saved"));
      } catch {
        toast.error("Could not load saved items");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <p className="text-sm text-muted-foreground">Loading…</p>;

  if (items.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Nothing saved yet. Saved items from Telegram or the digest will appear here.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <Card key={`${item.content_item_id}`}>
          <CardContent className="pt-6">
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="font-medium hover:underline"
            >
              {item.title}
            </a>
            <p className="mt-1 text-xs text-muted-foreground">
              via {item.source_name ?? "unknown"} · saved {new Date(item.saved_at).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
