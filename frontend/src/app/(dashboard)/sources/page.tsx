import { SourcesView } from "@/components/sources-view";

export const metadata = { title: "Sources · Tech Radar" };

export default function SourcesPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Sources</h1>
        <p className="text-sm text-muted-foreground">
          RSS feeds, Hacker News, and GitHub repositories the collector pulls from.
        </p>
      </div>
      <SourcesView />
    </div>
  );
}
