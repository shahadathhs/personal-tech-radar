import { Suspense } from "react";
import { TodayDigest } from "@/components/today-digest";

export const metadata = { title: "Today · Tech Radar" };

export default function TodayPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Today&apos;s Digest</h1>
        <p className="text-sm text-muted-foreground">
          What happened, why it matters, and why you should care.
        </p>
      </div>
      <Suspense fallback={<p className="text-sm text-muted-foreground">Loading…</p>}>
        <TodayDigest />
      </Suspense>
    </div>
  );
}
