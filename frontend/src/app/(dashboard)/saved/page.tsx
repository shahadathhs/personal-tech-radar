import { SavedList } from "@/components/saved-list";

export const metadata = { title: "Saved · Tech Radar" };

export default function SavedPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Saved</h1>
        <p className="text-sm text-muted-foreground">Items you bookmarked from your digests.</p>
      </div>
      <SavedList />
    </div>
  );
}
