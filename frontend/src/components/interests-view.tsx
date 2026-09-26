"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Interest, Profile } from "@/lib/types";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

export function InterestsView() {
  const [interests, setInterests] = useState<Interest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const profile = await api<Profile>("/api/profile");
        setInterests(profile.interests);
      } catch {
        toast.error("Could not load interests");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const refresh = useCallback(async () => {
    try {
      const profile = await api<Profile>("/api/profile");
      setInterests(profile.interests);
    } catch {
      toast.error("Could not load interests");
    }
  }, []);

  const remove = async (interest: Interest) => {
    try {
      await api(`/api/profile/interests/${interest.id}`, { method: "DELETE" });
      await refresh();
    } catch {
      toast.error("Delete failed");
    }
  };

  if (loading) return <p className="text-sm text-muted-foreground">Loading…</p>;

  const roots = interests.filter((i) => !i.parent_name);
  const childrenOf = (name: string) => interests.filter((i) => i.parent_name === name);

  return (
    <div className="space-y-6">
      <AddInterestForm onAdded={refresh} />
      {roots.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No interests yet. Add topics like AI, Backend, or Infrastructure — the digest
          personalization depends on them.
        </p>
      ) : (
        roots.map((root) => (
          <Card key={root.id}>
            <CardContent className="space-y-3 pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{root.name}</span>
                  <Badge variant="outline">weight {root.weight}</Badge>
                  {!root.enabled && <Badge variant="secondary">disabled</Badge>}
                </div>
                <Button variant="ghost" size="sm" onClick={() => remove(root)}>
                  Remove
                </Button>
              </div>
              {childrenOf(root.name).length > 0 && (
                <div className="flex flex-wrap gap-2 pl-4">
                  {childrenOf(root.name).map((child) => (
                    <button
                      key={child.id}
                      onClick={() => remove(child)}
                      className="rounded-full border px-3 py-1 text-xs text-muted-foreground hover:border-destructive hover:text-destructive"
                      title="Click to remove"
                    >
                      {child.name} ×
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}

function AddInterestForm({ onAdded }: { onAdded: () => void }) {
  const [name, setName] = useState("");
  const [parentName, setParentName] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api("/api/profile/interests", {
        method: "POST",
        body: JSON.stringify({ name, parent_name: parentName || null }),
      });
      toast.success(`Added ${name}`);
      setName("");
      setParentName("");
      onAdded();
    } catch {
      toast.error("Could not add interest");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="grid gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
      <div className="space-y-2">
        <Label htmlFor="interest-name">Interest</Label>
        <Input
          id="interest-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="LLMs"
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="interest-parent">Parent (optional)</Label>
        <Input
          id="interest-parent"
          value={parentName}
          onChange={(e) => setParentName(e.target.value)}
          placeholder="AI"
        />
      </div>
      <Button type="submit" disabled={submitting}>
        {submitting ? "Adding…" : "Add interest"}
      </Button>
    </form>
  );
}
