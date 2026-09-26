"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export function SettingsForm() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setProfile(await api<Profile>("/api/profile"));
      } catch {
        toast.error("Could not load profile");
      }
    })();
  }, []);

  if (!profile) return <p className="text-sm text-muted-foreground">Loading…</p>;

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      const updated = await api<Profile>("/api/profile", {
        method: "PUT",
        body: JSON.stringify({
          role: profile.role,
          experience_level: profile.experience_level,
          digest_time: profile.digest_time,
          digest_length: profile.digest_length,
          timezone: profile.timezone,
          excluded_topics: profile.excluded_topics,
          preferred_sources: profile.preferred_sources,
        }),
      });
      setProfile(updated);
      toast.success("Profile saved");
    } catch {
      toast.error("Save failed");
    } finally {
      setSaving(false);
    }
  };

  const set = (patch: Partial<Profile>) => setProfile({ ...profile, ...patch });

  return (
    <form onSubmit={save} className="space-y-6">
      <Card>
        <CardContent className="grid gap-4 pt-6 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Input
              id="role"
              value={profile.role}
              onChange={(e) => set({ role: e.target.value })}
              placeholder="software engineer"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="experience">Experience</Label>
            <Input
              id="experience"
              value={profile.experience_level}
              onChange={(e) => set({ experience_level: e.target.value })}
              placeholder="senior"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="digest-time">Digest time</Label>
            <Input
              id="digest-time"
              type="time"
              value={profile.digest_time}
              onChange={(e) => set({ digest_time: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="digest-length">Digest length</Label>
            <select
              id="digest-length"
              value={profile.digest_length}
              onChange={(e) => set({ digest_length: e.target.value })}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
            >
              <option value="short">short</option>
              <option value="normal">normal</option>
              <option value="deep">deep</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="timezone">Timezone</Label>
            <Input
              id="timezone"
              value={profile.timezone}
              onChange={(e) => set({ timezone: e.target.value })}
              placeholder="Asia/Dhaka"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="excluded">Excluded topics (comma separated)</Label>
            <Input
              id="excluded"
              value={profile.excluded_topics.join(", ")}
              onChange={(e) =>
                set({
                  excluded_topics: e.target.value
                    .split(",")
                    .map((t) => t.trim())
                    .filter(Boolean),
                })
              }
              placeholder="crypto, celebrity tech"
            />
          </div>
        </CardContent>
      </Card>
      <Button type="submit" disabled={saving}>
        {saving ? "Saving…" : "Save profile"}
      </Button>
    </form>
  );
}
