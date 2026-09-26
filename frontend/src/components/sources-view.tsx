"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Source } from "@/lib/types";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

export function SourcesView() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setSources(await api<Source[]>("/api/sources"));
      } catch {
        toast.error("Could not load sources");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const refresh = useCallback(async () => {
    try {
      setSources(await api<Source[]>("/api/sources"));
    } catch {
      toast.error("Could not load sources");
    }
  }, []);

  const toggle = async (source: Source) => {
    try {
      await api(`/api/sources/${source.id}`, {
        method: "PATCH",
        body: JSON.stringify({ enabled: !source.enabled }),
      });
      await refresh();
    } catch {
      toast.error("Update failed");
    }
  };

  const remove = async (source: Source) => {
    try {
      await api(`/api/sources/${source.id}`, { method: "DELETE" });
      toast.success(`Removed ${source.name}`);
      await refresh();
    } catch {
      toast.error("Delete failed");
    }
  };

  if (loading) return <p className="text-sm text-muted-foreground">Loading…</p>;

  return (
    <div className="space-y-6">
      <AddSourceForm onAdded={refresh} />
      {sources.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No sources yet — add one above, they are also seeded on first collect.
        </p>
      ) : (
        sources.map((s) => (
          <Card key={s.id}>
            <CardContent className="flex items-center justify-between gap-4 pt-6">
              <div className="min-w-0 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="truncate font-medium">{s.name}</span>
                  <Badge variant="outline">{s.source_type}</Badge>
                  {s.enabled ? <Badge>enabled</Badge> : <Badge variant="secondary">off</Badge>}
                </div>
                <p className="truncate text-xs text-muted-foreground">{s.url}</p>
                <p className="text-xs text-muted-foreground">
                  quality {s.quality_weight.toFixed(2)} · last collected{" "}
                  {s.last_collected_at ? new Date(s.last_collected_at).toLocaleString() : "never"}
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <Button variant="outline" size="sm" onClick={() => toggle(s)}>
                  {s.enabled ? "Disable" : "Enable"}
                </Button>
                <Button variant="destructive" size="sm" onClick={() => remove(s)}>
                  Remove
                </Button>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}

function AddSourceForm({ onAdded }: { onAdded: () => void }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [type, setType] = useState("rss");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api("/api/sources", {
        method: "POST",
        body: JSON.stringify({ name, url, source_type: type }),
      });
      toast.success(`Added ${name}`);
      setName("");
      setUrl("");
      onAdded();
    } catch {
      toast.error("Could not add source");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="grid gap-4 sm:grid-cols-[1fr_1fr_auto_auto] sm:items-end">
      <div className="space-y-2">
        <Label htmlFor="source-name">Name</Label>
        <Input
          id="source-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="hacker-news"
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="source-url">URL</Label>
        <Input
          id="source-url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/feed.xml"
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="source-type">Type</Label>
        <select
          id="source-type"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
        >
          <option value="rss">rss</option>
          <option value="hackernews">hackernews</option>
          <option value="github">github</option>
        </select>
      </div>
      <Button type="submit" disabled={submitting}>
        {submitting ? "Adding…" : "Add source"}
      </Button>
    </form>
  );
}
